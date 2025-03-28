from typing import Union, Optional
from .sdk import SaladCloudTranscriptionSdk
from .services.async_.transcription import TranscriptionServiceAsync
from .models.transcription_request import TranscriptionRequest
from salad_cloud_sdk.models import InferenceEndpointJob, InferenceEndpointJobCollection
from .net.environment import Environment


class SaladCloudTranscriptionSdkAsync(SaladCloudTranscriptionSdk):
    """
    SaladCloudTranscriptionSdkAsync is the asynchronous version of the SaladCloudTranscriptionSdk.
    """

    def __init__(
        self,
        api_key: str = None,
        api_key_header: str = "Salad-Api-Key",
        base_url: Union[Environment, str] = Environment.DEFAULT_SALAD_API_URL,
        timeout: int = 60000,
    ):
        """
        Initializes SaladCloudTranscriptionSdkAsync class.
        """
        super().__init__(
            api_key=api_key,
            api_key_header=api_key_header,
            base_url=base_url,
            timeout=timeout,
        )

        self.transcription = TranscriptionServiceAsync(
            base_url=self._base_url, api_key=api_key
        )

        self.set_api_key(api_key, api_key_header)
        self.set_timeout(timeout)
