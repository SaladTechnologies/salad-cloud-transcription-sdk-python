from typing import Optional, Union, Any
from enum import Enum

from ..simple_storage import SimpleStorageService, HttpMethod
from ..utils.base_service import BaseService
from ...net.environment.environment import Environment
from ...models.file_operation_response import FileOperationResponse
from .utils.to_async import to_async


class SimpleStorageServiceAsync(SimpleStorageService):
    """Asynchronous service for interacting with Salad Cloud Simple Storage Service"""

    def __init__(
        self,
        base_url: Union[Environment, str] = Environment.DEFAULT_S4_URL,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Initializes an asynchronous SimpleStorageService instance.

        :param base_url: The base URL for the service. Defaults to Environment.DEFAULT_S4_URL.
        :type base_url: Union[Environment, str]
        :param api_key: The API key for authentication.
        :type api_key: Optional[str]
        """
        super().__init__(base_url=base_url, api_key=api_key)

        # Convert methods to async
        self.upload_file = to_async(self.upload_file)
        self.delete_file = to_async(self.delete_file)
        self.sign_url = to_async(self.sign_url)
