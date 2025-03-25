import json
import os
import time
from typing import Dict, Any, Union, Optional
from urllib.parse import urlparse

from salad_cloud_sdk import SaladCloudSdk
from salad_cloud_sdk.models import (
    InferenceEndpointJobPrototype,
    InferenceEndpointJob,
    Status,
)
from .utils.validator import Validator
from .utils.base_service import BaseService
from .utils.webhooks import Webhook, WebhookVerificationError
from ..net.transport.serializer import Serializer
from ..models.transcription_request import TranscriptionRequest
from .simple_storage import SimpleStorageService
from ..net.environment.environment import Environment, TRANSCRIPTION_ENDPOINT_NAME


class TranscriptionService(BaseService):
    """Service for interacting with Salad Cloud Transcription API"""

    def __init__(
        self,
        base_url: Union[Environment, str] = Environment.DEFAULT_SALAD_API_URL,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Initializes a TranscriptionService instance.

        :param base_url: The base URL the service is using. Defaults to Environment.DEFAULT_SALAD_API_URL.
        :type base_url: Union[Environment, str]
        :param api_key: The API key for authentication.
        :type api_key: Optional[str]
        """
        self._base_url = (
            base_url.value if isinstance(base_url, Environment) else base_url
        )
        super().__init__(base_url)

        if api_key:
            self.set_api_key(api_key)

        self._storage_service = SimpleStorageService(api_key=api_key)
        self._salad_sdk = SaladCloudSdk(api_key=api_key, base_url=base_url)

    def transcribe(
        self,
        source: str,
        organization_name: str,
        request: TranscriptionRequest,
        auto_poll: bool = False,
    ) -> InferenceEndpointJob:
        """Creates a new transcription job

        :param source: The file to transcribe - can be a URL (http/https) or a local file path
        :type source: str
        :param organization_name: Your organization name. This identifies the billing context for the API operation.
        :type organization_name: str
        :param request: The transcription request options
        :type request: TranscriptionRequest
        :param auto_poll: Whether to block until the transcription is complete, or return immediately
        :type auto_poll: bool, optional (default=False)

        :raises RequestError: Raised when a request fails.
        :raises ValueError: Raised when input parameters are invalid.

        :return: The transcription job details
        :rtype: InferenceEndpointJob
        """

        Validator(str).min_length(2).max_length(63).pattern(
            "^[a-z][a-z0-9-]{0,61}[a-z0-9]$"
        ).validate(organization_name)

        # Get the source file URL (also uploads the file to S4 if it's local)
        file_url = self._process_source(source, organization_name)

        request_dict = request.to_dict()["input"]
        request_dict["url"] = file_url

        job_prototype = InferenceEndpointJobPrototype(
            input=request_dict,
            webhook=request.webhook,
            webhook_url=request.webhook,
        )

        print(job_prototype)

        # Use Salad SDK inference service to create the actual job
        inference_endpoint_name = TRANSCRIPTION_ENDPOINT_NAME
        response = self._salad_sdk.inference_endpoints.create_inference_endpoint_job(
            request_body=job_prototype,
            organization_name=organization_name,
            inference_endpoint_name=inference_endpoint_name,
        )

        # If auto_poll is enabled, let's wait for the transcription to complete
        # Polls every 5 seconds, if enabled
        if auto_poll:
            job_id = response.id_
            while True:
                job = self.get_transcription_job(organization_name, job_id)
                if job.status in [
                    Status.SUCCEEDED.value,
                    Status.FAILED.value,
                    Status.CANCELLED.value,
                ]:
                    return job
                time.sleep(5)

        return response

    def _process_source(self, source: str, organization_name: str) -> str:
        """Process the source to determine if it's a URL or local file and handle accordingly

        :param source: The file to transcribe - can be a URL or local file path
        :type source: str
        :param organization_name: The organization name
        :type organization_name: str

        :raises ValueError: If the source is invalid (invalid URL)
        :return: A valid URL pointing to the content
        :rtype: str
        """
        # Check if it's a URL
        parsed_url = urlparse(source)
        if parsed_url.scheme in ("http", "https") and parsed_url.netloc:
            return source
        else:
            # It's a local file path - let the storage service handle file existence check and opening
            upload_response = self._storage_service.upload_file(
                organization_name=organization_name, local_file_path=source
            )

            return upload_response.url

    def get_transcription_job(
        self, organization_name: str, job_id: str
    ) -> InferenceEndpointJob:
        """Get a transcription job by providing the inference job ID

        :param organization_name: The organization name
        :type organization_name: str
        :param job_id: The transcription job ID
        :type job_id: str

        :return: The transcription job details
        :rtype: InferenceEndpointJob
        """
        inference_endpoint_name = TRANSCRIPTION_ENDPOINT_NAME
        return self._salad_sdk.inference_endpoints.get_inference_endpoint_job(
            organization_name=organization_name,
            inference_endpoint_name=inference_endpoint_name,
            inference_endpoint_job_id=job_id,
        )

    def list_transcription_jobs(
        self,
        organization_name: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ):
        """Lists all transcription jobs for an organization

        :param organization_name: The organization name
        :type organization_name: str
        :param page: The page number, defaults to None
        :type page: Optional[int], optional
        :param page_size: The maximum number of items per page, defaults to None
        :type page_size: Optional[int], optional

        :return: Collection of transcription jobs
        :rtype: InferenceEndpointJobCollection
        """
        inference_endpoint_name = TRANSCRIPTION_ENDPOINT_NAME
        return self._salad_sdk.inference_endpoints.list_inference_endpoint_jobs(
            organization_name=organization_name,
            inference_endpoint_name=inference_endpoint_name,
            page=page,
            page_size=page_size,
        )

    def delete_transcription_job(self, organization_name: str, job_id: str) -> None:
        """Cancels a transcription job

        :param organization_name: The organization name
        :type organization_name: str
        :param job_id: The transcription job ID
        :type job_id: str

        :raises RequestError: Raised when a request fails.
        """
        inference_endpoint_name = TRANSCRIPTION_ENDPOINT_NAME
        self._salad_sdk.inference_endpoints.delete_inference_endpoint_job(
            organization_name=organization_name,
            inference_endpoint_name=inference_endpoint_name,
            inference_endpoint_job_id=job_id,
        )

    def process_webhook_request(
        self,
        payload: Any,
        signing_secret: str,
        webhook_id: str,
        webhook_timestamp: str,
        webhook_signature: str,
    ) -> InferenceEndpointJob:
        """Process a webhook request from Salad Cloud Transcription service.

        :param payload: The webhook request payload (string or bytes)
        :type payload: Any
        :param signing_secret: The secret used for verifying the webhook signature
        :type signing_secret: str
        :param webhook_id: The webhook ID from the request header
        :type webhook_id: str
        :param webhook_timestamp: The timestamp from the request header
        :type webhook_timestamp: str
        :param webhook_signature: The signature from the request header
        :type webhook_signature: str

        :raises WebhookVerificationError: If signature validation fails

        :return: The processed job result
        :rtype: InferenceEndpointJob
        """
        # Create headers dictionary for verification
        headers = {
            "webhook-id": webhook_id,
            "webhook-timestamp": webhook_timestamp,
            "webhook-signature": webhook_signature,
        }

        # Initialize webhook validator with the signing secret
        webhook = Webhook(signing_secret)

        # Verify the payload signature
        # This will raise WebhookVerificationError if validation fails
        job_data = webhook.verify(payload, headers)

        return InferenceEndpointJob._unmap(job_data)
