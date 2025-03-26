import asyncio
from typing import Optional, Union, Any

from salad_cloud_sdk.models import (
    InferenceEndpointJob,
    InferenceEndpointJobPrototype,
    Status,
)
from ..utils.validator import Validator
from ..transcription import TranscriptionService
from ...net.environment.environment import TRANSCRIPTION_ENDPOINT_NAME, Environment
from ...models.transcription_request import TranscriptionRequest
from .simple_storage import SimpleStorageServiceAsync
from .utils.to_async import to_async


class TranscriptionServiceAsync(TranscriptionService):
    """Asynchronous service for interacting with Salad Cloud Transcription API"""

    def __init__(
        self,
        base_url: Union[Environment, str] = Environment.DEFAULT_SALAD_API_URL,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Initializes an asynchronous TranscriptionService instance.

        :param base_url: The base URL the service is using. Defaults to Environment.DEFAULT_SALAD_API_URL.
        :type base_url: Union[Environment, str]
        :param api_key: The API key for authentication.
        :type api_key: Optional[str]
        """
        super().__init__(base_url=base_url, api_key=api_key)

        # Convert methods to async
        self.get_transcription_job = to_async(self.get_transcription_job)
        self.list_transcription_jobs = to_async(self.list_transcription_jobs)
        self.delete_transcription_job = to_async(self.delete_transcription_job)
        self.process_webhook_request = to_async(self.process_webhook_request)

    async def transcribe(
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
                job = await self.get_transcription_job(organization_name, job_id)
                if job.status in [
                    Status.SUCCEEDED.value,
                    Status.FAILED.value,
                    Status.CANCELLED.value,
                ]:
                    return job
                await asyncio.sleep(5)

        return response
