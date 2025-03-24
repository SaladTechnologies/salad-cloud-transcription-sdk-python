import os
import json
import requests
from pathlib import Path
from enum import Enum
from typing import Optional, BinaryIO, Union, IO, Dict, List, Any

from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..net.environment.environment import Environment
from ..models.file_upload_response import FileUploadResponse


class HttpMethod(Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class SimpleStorageService(BaseService):
    MAX_FILE_SIZE = 100 * 1024 * 1024
    DEFAULT_CHUNK_SIZE = 80 * 1024 * 1024
    # Default signature expiration in seconds (5 days)
    DEFAULT_SIGNATURE_EXP = 432000

    def __init__(
        self,
        base_url: Union[Environment, str] = Environment.DEFAULT_S4_URL,
        api_key: Optional[str] = None,
    ) -> None:
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
        local_file_path: str,
        mime_type: Optional[str] = None,
        sign: bool = True,
        signature_exp: Optional[int] = DEFAULT_SIGNATURE_EXP,
    ) -> FileUploadResponse:
        """Uploads a file to the Salad Cloud Storage Service

        :param organization_name: Your organization name. This identifies the billing context for the API operation and represents a security boundary for SaladCloud resources. The organization must be created before using the API, and you must be a member of the organization.
        :type organization_name: str
        :param local_file_path: The local path to the file to be uploaded
        :type local_file_path: str
        :param mime_type: The MIME type of the file. If not provided, it will be determined automatically.
        :type mime_type: Optional[str]
        :param sign: Whether to sign the URL, defaults to True
        :type sign: bool
        :param signature_exp: The expiration time for the signature in seconds, defaults to 5 days (432000 seconds)
        :type signature_exp: Optional[int]

        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        :raises ValueError: If the file doesn't exist.

        :return: Response containing the URL where the file can be accessed
        :rtype: FileUploadResponse
        """

        print(local_file_path)

        Validator(str).min_length(2).max_length(63).pattern(
            "^[a-z][a-z0-9-]{0,61}[a-z0-9]$"
        ).validate(organization_name)
        Validator(str).validate(local_file_path)

        # Check if file exists
        if not os.path.exists(local_file_path):
            raise ValueError(f"File not found: {local_file_path}")

        # Extract filename from path
        filename = os.path.basename(local_file_path)

        # Determine MIME type if not provided
        if mime_type is None:
            mime_type = self._determine_mime_type(filename)
        else:
            Validator(str).validate(mime_type)

        # Get file size
        file_size = Path(local_file_path).stat().st_size

        # For small files, use regular upload
        if file_size <= self.MAX_FILE_SIZE:
            return self._upload_file_direct(
                organization_name=organization_name,
                local_file_path=local_file_path,
                filename=filename,
                mime_type=mime_type,
                sign=sign,
                signature_exp=signature_exp,
            )
        # For large files, use multipart upload
        else:
            return self._upload_file_in_parts(
                organization_name=organization_name,
                local_file_path=local_file_path,
                filename=filename,
                mime_type=mime_type,
                sign=sign,
                signature_exp=signature_exp,
            )

    def _upload_file_direct(
        self,
        organization_name: str,
        local_file_path: str,
        filename: str,
        mime_type: str,
        sign: bool = True,
        signature_exp: Optional[int] = DEFAULT_SIGNATURE_EXP,
    ) -> FileUploadResponse:
        """Directly uploads a file to Salad Cloud Storage (for files <= MAX_FILE_SIZE)

        :param organization_name: Organization name
        :param local_file_path: Local file path
        :param filename: Filename to use in storage
        :param mime_type: MIME type
        :param sign: Whether to sign the URL
        :param signature_exp: Expiration time for signature
        :return: Response containing the URL where the file can be accessed
        :rtype: FileUploadResponse
        """
        # Open the file for upload
        with open(local_file_path, "rb") as file:
            file_content = file.read()

            # Create multipart form data
            body = {"file_name": filename, "sign": sign, "file": file_content}

            if signature_exp is not None:
                Validator(int).min(1).validate(signature_exp)
                body["signatureExp"] = signature_exp

            serialized_request = (
                Serializer(
                    f"{self.base_url}/organizations/{{organization_name}}/files/{{filename}}",
                    [self.get_api_key()],
                )
                .add_path("organization_name", organization_name)
                .add_path("filename", filename)
                .serialize()
                .set_method("PUT")
                .set_body(body, "multipart/form-data")
            )

            response, _, _ = self.send_request(serialized_request)
            return FileUploadResponse._unmap(response)

    def _upload_file_in_parts(
        self,
        organization_name: str,
        local_file_path: str,
        filename: str,
        mime_type: str,
        sign: bool = True,
        signature_exp: Optional[int] = DEFAULT_SIGNATURE_EXP,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> FileUploadResponse:
        """Uploads a large file in parts (multipart upload)

        :param organization_name: Organization name
        :param local_file_path: Local file path
        :param filename: Filename to use in storage
        :param mime_type: MIME type
        :param sign: Whether to sign the URL
        :param signature_exp: Expiration time for signature
        :param chunk_size: Size of each chunk in bytes (default 80MB)
        :return: Response containing the URL where the file can be accessed
        :rtype: FileUploadResponse
        """
        # Query parameters for creating MPU
        query_params = {}
        if sign:
            query_params["sign"] = "true"
            if signature_exp:
                query_params["signatureExp"] = signature_exp
        if mime_type:
            query_params["mimeType"] = mime_type

        # Step 1: Create multipart upload
        serialized_create_request = (
            Serializer(
                f"{self.base_url}/organizations/{{organization_name}}/files/{{filename}}",
                [self.get_api_key()],
            )
            .add_path("organization_name", organization_name)
            .add_path("filename", filename)
            .add_query("action", "mpu-create")
            .serialize()
            .set_method("PUT")
        )

        create_response, _, _ = self.send_request(serialized_create_request)
        upload_id = create_response["uploadId"]

        # Step 2: Upload parts
        parts = []
        part_number = 1
        print(chunk_size)
        with open(local_file_path, "rb") as file:
            while True:
                chunk = file.read(int(chunk_size))
                if not chunk:
                    break

                serialized_chunk_request = (
                    Serializer(
                        f"{self.base_url}/organizations/{{organization_name}}/files/{{filename}}",
                        [self.get_api_key()],
                    )
                    .add_path("organization_name", organization_name)
                    .add_path("filename", filename)
                    .add_query("partNumber", part_number)
                    .add_query("uploadId", upload_id)
                    .serialize()
                    .set_method("PUT")
                    .set_body({"file": chunk}, "multipart/form-data")
                )

                chunk_response, _, _ = self.send_request(serialized_chunk_request)
                print(chunk_response)
                parts.append(
                    {"partNumber": part_number, "etag": chunk_response.get("etag", "")}
                )
                part_number += 1

        print(parts)

        # Step 3: Complete multipart upload
        serialized_complete_request = (
            Serializer(
                f"{self.base_url}/organizations/{{organization_name}}/files/{{filename}}",
                [self.get_api_key()],
            )
            .add_path("organization_name", organization_name)
            .add_path("filename", filename)
            .add_query("action", "mpu-complete")
            .add_query("uploadId", upload_id)
            .serialize()
            .set_method("PUT")
            .set_body({"parts": parts})
        )

        complete_response, _, _ = self.send_request(serialized_complete_request)
        return FileUploadResponse(url=complete_response["url"])

    def delete_file(
        self,
        organization_name: str,
        filename: str,
    ) -> bool:
        """Deletes a file from the Salad Cloud Storage Service

        :param organization_name: Your organization name. This identifies the billing context for the API operation and represents a security boundary for SaladCloud resources. The organization must be created before using the API, and you must be a member of the organization.
        :type organization_name: str
        :param filename: The name of the file to delete
        :type filename: str

        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.

        :return: True if the file was successfully deleted
        :rtype: bool
        """

        Validator(str).min_length(2).max_length(63).pattern(
            "^[a-z][a-z0-61}[a-z0-9]$"
        ).validate(organization_name)
        Validator(str).validate(filename)

        serialized_request = (
            Serializer(
                f"{self.base_url}/organizations/{{organization_name}}/files/{{filename}}",
                [self.get_api_key()],
            )
            .add_path("organization_name", organization_name)
            .add_path("filename", filename)
            .serialize()
            .set_method("DELETE")
        )

        _, status_code, _ = self.send_request(serialized_request)
        return status_code == 204

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
            "^[a-z][a-z0-9-]{0,61}[a-z0-9]$"
        ).validate(organization_name)
        Validator(str).validate(filename)
        Validator(int).min(1).validate(exp)

        # Convert enum to string if necessary
        if isinstance(method, HttpMethod):
            method = method.value
        else:
            Validator(str).validate(method)
            valid_methods = [m.value for m in HttpMethod]
            if method not in valid_methods:
                raise ValueError(f"Method must be one of {valid_methods}")

        request_body = {"method": method, "exp": exp}

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

    def _determine_mime_type(self, filename: str) -> str:
        """Determines the MIME type based on the file extension

        :param filename: The filename to determine the MIME type for
        :type filename: str

        :return: The MIME type
        :rtype: str
        """
        extension = os.path.splitext(filename)[1].lower()
        mime_map = {
            # Audio formats
            ".aiff": "audio/aiff",
            ".flac": "audio/flac",
            ".m4a": "audio/mp4",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            # Video formats
            ".mkv": "video/x-matroska",
            ".mov": "video/quicktime",
            ".webm": "video/webm",
            ".wma": "audio/x-ms-wma",
            ".mp4": "video/mp4",
        }
        return mime_map.get(extension, "application/octet-stream")
