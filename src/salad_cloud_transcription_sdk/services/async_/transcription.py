from typing import Optional, Union, Any

from ..utils.validator import Validator
from ..transcription import TranscriptionService
from ...net.environment.environment import Environment
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
        self.transcribe = to_async(self.transcribe)
        self.get_transcription_job = to_async(self.get_transcription_job)
        self.list_transcription_jobs = to_async(self.list_transcription_jobs)
        self.delete_transcription_job = to_async(self.delete_transcription_job)
        self.process_webhook_request = to_async(self.process_webhook_request)
