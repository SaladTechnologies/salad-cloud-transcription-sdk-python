import asyncio
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
from salad_cloud_transcription_sdk.models.transcription_webhook_payload import (
    TranscriptionWebhookPayload,
)
from .utils.validator import Validator
from .utils.base_service import BaseService
from .utils.webhooks import Webhook, WebhookVerificationError
from ..net.transport.serializer import Serializer
from ..models.transcription_request import TranscriptionRequest
from ..models.transcription_job_output import TranscriptionJobOutput
from ..models.transcription_job_file_output import TranscriptionJobFileOutput
from .simple_storage import SimpleStorageService
from ..net.environment.environment import (
    Environment,
    COMPLETE_TRANSCRIPTION_ENDPOINT_NAME,
    LITE_TRANSCRIPTION_ENDPOINT_NAME,
)
from ..models.transcription_engine import TranscriptionEngine


class TranscriptionService(BaseService):
    """Service for interacting with Salad Cloud Transcription API"""

    # Maximum polling duration in seconds (30 minutes)
    MAX_POLLING_DURATION = 1800

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
        _base_url = base_url.value if isinstance(base_url, Environment) else base_url

        super().__init__(_base_url)

        api_key = (api_key or "").strip()
        if not api_key:
            raise ValueError(
                "The API key cannot be empty. Retrieve your Salad API key and set it here."
            )

        self.set_api_key(api_key)
        self._storage_service = SimpleStorageService(api_key=api_key)
        self._salad_sdk = SaladCloudSdk(api_key=api_key, base_url=_base_url)

    def _get_endpoint_name(
        self, engine: TranscriptionEngine = TranscriptionEngine.Complete
    ) -> str:
        """Get the appropriate endpoint name based on the transcription engine

        :param engine: The transcription engine to use
        :type engine: TranscriptionEngine
        :return: The endpoint name
        :rtype: str
        """
        return (
            LITE_TRANSCRIPTION_ENDPOINT_NAME
            if engine == TranscriptionEngine.Lite
            else COMPLETE_TRANSCRIPTION_ENDPOINT_NAME
        )

    def transcribe(
        self,
        source: str,
        organization_name: str,
        request: TranscriptionRequest,
        engine: TranscriptionEngine = TranscriptionEngine.Complete,
        auto_poll: bool = False,
        max_polling_duration: int = MAX_POLLING_DURATION,
    ) -> InferenceEndpointJob:
        """Creates a new transcription job

        :param source: The file to transcribe - can be a URL (http/https) or a local file path
        :type source: str
        :param organization_name: Your organization name. This identifies the billing context for the API operation.
        :type organization_name: str
        :param request: The transcription request options
        :type request: TranscriptionRequest
        :param engine: The transcription engine to use (Complete or Lite)
        :type engine: TranscriptionEngine, optional (default=TranscriptionEngine.Complete)
        :param auto_poll: Whether to block until the transcription is complete, or return immediately
        :type auto_poll: bool, optional (default=False)
        :param max_polling_duration: Maximum duration in seconds to poll for job completion
        :type max_polling_duration: int, optional (default=1800 meaning 30 minutes)

        :raises RequestError: Raised when a request fails.
        :raises ValueError: Raised when input parameters are invalid.
        :raises TimeoutError: Raised when polling exceeds the maximum duration.

        :return: The transcription job details
        :rtype: InferenceEndpointJob
        """
        if source is None or not source.strip():
            raise ValueError("The source file path or URL cannot be empty.")

        if not isinstance(request, TranscriptionRequest):
            raise ValueError("The request must be an instance of TranscriptionRequest.")

        Validator(str).min_length(2).max_length(63).pattern(
            "^[a-z][a-z0-9-]{0,61}[a-z0-9]$"
        ).validate(organization_name)

        # Get the source file URL (also uploads the file to S4 if it's local)
        file_url = self._process_source(source, organization_name)

        request_dict = request.to_dict()["input"]
        request_dict["url"] = file_url

        if request.webhook is not None:
            job_prototype = InferenceEndpointJobPrototype(
                input=request_dict,
                webhook=request.webhook or None,
                webhook_url=request.webhook or None,
            )
        else:
            job_prototype = InferenceEndpointJobPrototype(
                input=request_dict,
            )

        # Choose the appropriate endpoint based on engine type
        inference_endpoint_name = self._get_endpoint_name(engine)

        # Use Salad SDK inference service to create the actual job
        response = self._salad_sdk.inference_endpoints.create_inference_endpoint_job(
            request_body=job_prototype,
            organization_name=organization_name,
            inference_endpoint_name=inference_endpoint_name,
        )

        job = response
        print(job.status)

        # If auto_poll is enabled, let's wait for the transcription to complete
        # Polls every 5 seconds, if enabled
        if auto_poll:
            job_id = response.id_
            start_time = time.time()

            while job.status not in [
                Status.SUCCEEDED.value,
                Status.FAILED.value,
                Status.CANCELLED.value,
            ]:
                print(job.status)
                # Check if we've exceeded the maximum polling duration
                if time.time() - start_time > max_polling_duration:
                    raise TimeoutError(
                        f"Transcription polling exceeded maximum duration of {max_polling_duration/60} minutes"
                    )

                job = self._get_transcription_job_internal(
                    organization_name, job_id, engine
                )
                time.sleep(5)

        # Convert job output to appropriate type if possible
        self._convert_job_output(job)

        return job

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
        self,
        organization_name: str,
        job_id: str,
        engine: TranscriptionEngine = TranscriptionEngine.Complete,
    ) -> InferenceEndpointJob:
        """Get a transcription job by providing the inference job ID

        :param organization_name: The organization name
        :type organization_name: str
        :param job_id: The transcription job ID
        :type job_id: str
        :param engine: The transcription engine to use
        :type engine: TranscriptionEngine, optional (default=TranscriptionEngine.Complete)

        :return: The transcription job details
        :rtype: InferenceEndpointJob
        """
        return self._get_transcription_job_internal(organization_name, job_id, engine)

    def _get_transcription_job_internal(
        self,
        organization_name: str,
        job_id: str,
        engine: TranscriptionEngine = TranscriptionEngine.Complete,
    ) -> InferenceEndpointJob:
        inference_endpoint_name = self._get_endpoint_name(engine)
        job = self._salad_sdk.inference_endpoints.get_inference_endpoint_job(
            organization_name=organization_name,
            inference_endpoint_name=inference_endpoint_name,
            inference_endpoint_job_id=job_id,
        )

        # Convert job output to appropriate type if possible
        self._convert_job_output(job)
        return job

    def list_transcription_jobs(
        self,
        organization_name: str,
        engine: TranscriptionEngine = TranscriptionEngine.Complete,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ):
        """Lists all transcription jobs for an organization

        :param organization_name: The organization name
        :type organization_name: str
        :param engine: The transcription engine to use
        :type engine: TranscriptionEngine, optional (default=TranscriptionEngine.Complete)
        :param page: The page number, defaults to None
        :type page: Optional[int], optional
        :param page_size: The maximum number of items per page, defaults to None
        :type page_size: Optional[int], optional

        :return: Collection of transcription jobs
        :rtype: InferenceEndpointJobCollection
        """
        inference_endpoint_name = self._get_endpoint_name(engine)
        return self._salad_sdk.inference_endpoints.list_inference_endpoint_jobs(
            organization_name=organization_name,
            inference_endpoint_name=inference_endpoint_name,
            page=page,
            page_size=page_size,
        )

    def delete_transcription_job(
        self,
        organization_name: str,
        job_id: str,
        engine: TranscriptionEngine = TranscriptionEngine.Complete,
    ) -> None:
        """Cancels a transcription job

        :param organization_name: The organization name
        :type organization_name: str
        :param job_id: The transcription job ID
        :type job_id: str
        :param engine: The transcription engine to use
        :type engine: TranscriptionEngine, optional (default=TranscriptionEngine.Complete)

        :raises RequestError: Raised when a request fails.
        """
        inference_endpoint_name = self._get_endpoint_name(engine)
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
    ) -> TranscriptionWebhookPayload:
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
        if webhook.verify(payload, headers):
            deserialized_payload = TranscriptionWebhookPayload.from_json(payload)
            deserialized_payload.data = self._convert_job_output(
                deserialized_payload.data
            )
            return deserialized_payload

        raise WebhookVerificationError("Signature validation failed.")

    def _convert_job_output(self, job: InferenceEndpointJob) -> InferenceEndpointJob:
        """Converts job output to appropriate output model if possible

        :param job: The job with output to convert
        :type job: InferenceEndpointJob
        :return: The job with converted output
        :rtype: InferenceEndpointJob
        """
        if hasattr(job, "output") and job.output is not None:
            try:
                job.output = TranscriptionJobOutput.from_json(job.output)
            except (ValueError, KeyError, TypeError) as e:
                print(f"Error converting to TranscriptionJobOutput: {e}")
                try:
                    job.output = TranscriptionJobFileOutput.from_json(job.output)
                except (ValueError, KeyError, TypeError) as e:
                    print(f"Error converting to TranscriptionJobFileOutput: {e}")
                    # If conversion fails, leave the output as is
                    pass
        return job
