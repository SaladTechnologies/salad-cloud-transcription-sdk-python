from enum import Enum
from typing import Optional, BinaryIO, Union, IO

from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..net.environment.environment import Environment


class HttpMethod(Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class SimpleStorageService(BaseService):  # Fixed class name typo: SimpleStoraegService -> SimpleStorageService

    def __init__(self, base_url: Union[Environment, str] = Environment.DEFAULT_S4_URL, api_key: Optional[str] = None) -> None:
        """
        Initializes a SimpleStorageService instance.

        :param base_url: The base URL for the service. Defaults to Environment.DEFAULT_S4_URL.
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

    def upload_file(
        self,
        organization_name: str,
        filename: str,
        file: Union[BinaryIO, IO[bytes]],
        mime_type: str,
        sign: bool = False,
        signature_exp: Optional[int] = None,
    ) -> str:
        """Uploads a file to the Salad Cloud Storage Service

        :param organization_name: Your organization name. This identifies the billing context for the API operation and represents a security boundary for SaladCloud resources. The organization must be created before using the API, and you must be a member of the organization.
        :type organization_name: str
        :param filename: The filename
        :type filename: str
        :param file: The file blob to upload
        :type file: Union[BinaryIO, IO[bytes]]
        :param mime_type: The MIME type of the file
        :type mime_type: str
        :param sign: Whether to sign the URL
        :type sign: bool
        :param signature_exp: The expiration time for the signature in seconds
        :type signature_exp: Optional[int]
        
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        
        :return: The URL where the file can be accessed
        :rtype: str
        """

        Validator(str).min_length(2).max_length(63).pattern(
            "^[a-z][a-z0-9-]{0,61}[a-z0-9]$"
        ).validate(organization_name)
        Validator(str).validate(filename)
        Validator(str).validate(mime_type)
        
        # Create multipart form data
        form_data = {
            'file': file,
            'mimeType': mime_type,
            'sign': sign
        }
        
        if signature_exp is not None:
            Validator(int).min_value(1).validate(signature_exp)
            form_data['signatureExp'] = signature_exp

        serialized_request = (
            Serializer(
                f"{self.base_url}/organizations/{{organization_name}}/files/{{filename}}",
                [self.get_api_key()],
            )
            .add_path("organization_name", organization_name)
            .add_path("filename", filename)
            .serialize()
            .set_method("PUT")
            .set_multipart_form(form_data)
        )

        response, _, _ = self.send_request(serialized_request)
        return response

    @cast_models
    def sign_url(
        self,
        organization_name: str,
        filename: str,
        method: Union[HttpMethod, str],
        exp: int,
    ) -> str:
        """Signs an URL

        :param organization_name: Your organization name. This identifies the billing context for the API operation and represents a security boundary for SaladCloud resources. The organization must be created before using the API, and you must be a member of the organization.
        :type organization_name: str
        :param filename: The filename
        :type filename: str
        :param method: The HTTP method to sign the URL for. Currently only supports GET
        :type method: Union[HttpMethod, str]
        :param exp: The expiration ttl of the signed URL in seconds
        :type exp: int
        
        """

        Validator(str).min_length(2).max_length(63).pattern(
            "^[a-z][a-z0-61}[a-z0-9]$"
        ).validate(organization_name)
        Validator(str).validate(filename)
        Validator(int).min_value(1).validate(exp)
        
        # Convert enum to string if necessary
        if isinstance(method, HttpMethod):
            method = method.value
        else:
            Validator(str).validate(method)
            valid_methods = [m.value for m in HttpMethod]
            if method not in valid_methods:
                raise ValueError(f"Method must be one of {valid_methods}")

        request_body = {
            "method": method,
            "exp": exp
        }

        serialized_request = (
            Serializer(
                f"{self.base_url}/organizations/{{organization_name}}/file_tokens/{{filename}}",
                [self.get_api_key()],
            )
            .add_path("organization_name", organization_name)
            .add_path("filename", filename)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response, _, _ = self.send_request(serialized_request)
        return response
