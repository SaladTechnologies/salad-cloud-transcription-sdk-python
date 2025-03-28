from typing import Union, Optional
from .services.transcription import TranscriptionService
from .models.transcription_request import TranscriptionRequest
from salad_cloud_sdk.models import InferenceEndpointJob, InferenceEndpointJobCollection

from .net.environment import Environment


class SaladCloudTranscriptionSdk:
    def __init__(
        self,
        api_key: str = None,
        api_key_header: str = "Salad-Api-Key",
        base_url: Union[Environment, str] = Environment.DEFAULT_SALAD_API_URL,
        timeout: int = 60000,
    ):
        """
        Initializes SaladCloudTranscriptionSdk class.
        """

        self._base_url = (
            base_url.value if isinstance(base_url, Environment) else base_url
        )
        
        self.transcription = TranscriptionService(base_url=self._base_url, api_key=api_key)
        
        self.set_api_key(api_key, api_key_header)
        self.set_timeout(timeout)

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
        
        :return: The transcription job details
        :rtype: InferenceEndpointJob
        """
        return self.transcription.transcribe(
            source=source,
            organization_name=organization_name,
            request=request,
            auto_poll=auto_poll
        )
    
    def get_transcription_job(self, organization_name: str, job_id: str) -> InferenceEndpointJob:
        """Get the status of a transcription job

        :param organization_name: The organization name
        :type organization_name: str
        :param job_id: The transcription job ID
        :type job_id: str
        
        :return: The transcription job details
        :rtype: InferenceEndpointJob
        """
        return self.transcription.get_transcription_job(
            organization_name=organization_name,
            job_id=job_id
        )
    
    def delete_transcription_job(self, organization_name: str, job_id: str) -> None:
        """Cancels a transcription job

        :param organization_name: The organization name
        :type organization_name: str
        :param job_id: The transcription job ID
        :type job_id: str
        """
        return self.transcription.delete_transcription_job(
            organization_name=organization_name,
            job_id=job_id
        )
    
    def list_transcription_jobs(
        self, 
        organization_name: str, 
        page: Optional[int] = None, 
        page_size: Optional[int] = None
    ) -> InferenceEndpointJobCollection:
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
        return self.transcription.list_transcription_jobs(
            organization_name=organization_name,
            page=page,
            page_size=page_size
        )

    def set_base_url(self, base_url: Union[Environment, str]):
        """
        Sets the base URL for the entire SDK.

        :param Union[Environment, str] base_url: The base URL to be set.
        :return: The SDK instance.
        """
        self._base_url = (
            base_url.value if isinstance(base_url, Environment) else base_url
        )

        self.transcription.set_base_url(self._base_url)

        return self

    def set_api_key(self, api_key: str, api_key_header="Salad-Api-Key"):
        """
        Sets the api key and the api key header for the entire SDK.
        """
        self.transcription.set_api_key(api_key, api_key_header)

        return self

    def set_timeout(self, timeout: int):
        """
        Sets the timeout for the entire SDK.

        :param int timeout: The timeout (ms) to be set.
        :return: The SDK instance.
        """
        self.transcription.set_timeout(timeout)

        return self
