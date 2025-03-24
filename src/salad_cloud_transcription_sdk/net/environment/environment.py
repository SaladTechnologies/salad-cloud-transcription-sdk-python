"""
An enum class containing all the possible environments for the SDK
"""

from enum import Enum
from urllib.parse import urlparse

TRANSCRIPTION_ENDPOINT_NAME = "transcription"

class Environment(Enum):
    """The environments available for the SDK"""

    DEFAULT_SALAD_API_URL = "https://api.salad.com/api/public"
    DEFAULT_S4_URL = "https://storage-api.salad.com"

    def __new__(cls, url):
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError(
                f"Environment url [{url}] is not valid. Please use the following format https://api.example.com"
            )

        obj = object.__new__(cls)
        obj._value_ = url
        obj._url = url
        return obj

    @property
    def url(self):
        """Get the base URL for this environment"""
        return self._url
