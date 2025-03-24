from typing import Any, BinaryIO, Optional, Set, Dict, Tuple
from .utils import extract_original_data
import mimetypes

FilesType = Dict[str, Tuple[Optional[str], BinaryIO, Optional[str]]]


class Request:
    """
    A simple HTTP request builder class using the requests library.

    Example Usage:
    ```python
    # Create a Request object
    request = Request()

    # Set request parameters
    request.set_url('https://yourendpoint.com/') \
           .set_method('GET') \
           .set_headers({'Content-Type': 'application/json'}) \
           .set_body(None)  # For GET requests, the body should be None

    # Send the HTTP request
    response = request.send()
    ```

    :ivar str url: The URL of the API endpoint.
    :ivar str method: The HTTP method for the request.
    :ivar dict headers: Dictionary of headers to include in the request.
    :ivar Any body: Request body.
    """

    def __init__(self):
        self.url = None
        self.method = None
        self.headers = None
        self.body = None
        self.scopes = None
        self.files = None

    def set_url(self, url: str) -> "Request":
        """
        Set the URL of the API endpoint.

        :param str url: The URL of the API endpoint.
        :return: The updated Request object.
        :rtype: Request
        """
        self.url = url
        return self

    def set_headers(self, headers: dict) -> "Request":
        """
        Set the headers for the HTTP request.

        :param dict headers: Dictionary of headers to include in the request.
        :return: The updated Request object.
        :rtype: Request
        """
        self.headers = headers
        return self

    def set_method(self, method: str) -> "Request":
        """
        Set the HTTP method for the request.

        :param str method: The HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE', etc.).
        :return: The updated Request object.
        :rtype: Request
        """
        self.method = method
        return self

    def set_body(self, body: Any, content_type: str = "application/json") -> "Request":
        """
        Set the request body (e.g., JSON payload).

        :param Any body: Request body.
        :param str content_type: The content type of the request body. Default is "application/json".
        :return: The updated Request object.
        :rtype: Request
        """
        self.body = extract_original_data(body)
        self.headers["Content-Type"] = content_type
        return self

    def set_scopes(self, scopes: Set[str]) -> "Request":
        """
        Set the scopes for the request.

        :param list scopes: List of scopes to include in the request.
        :return: The updated Request object.
        :rtype: Request
        """
        self.scopes = scopes
        return self

    def set_files(self, files: FilesType) -> "Request":
        """
        Sets the files  for multipart/form-data requests.

        :param files: Dictionary where keys are field names and values are tuples (filename, file_obj, mimetype).
        :return: The updated Request object.
        :rtype: Request
        """
        formatted_files = {}

        for key, value in files.items():
            if not isinstance(value, tuple) or len(value) < 2:
                raise ValueError(f"Invalid file tuple for key '{key}': {value}")

            filename, file_obj, *mime_type = value
            mime_type = (
                mime_type[0]
                if mime_type
                else mimetypes.guess_type(filename or "")[0]
                or "application/octet-stream"
            )

            formatted_files[key] = (filename, file_obj, mime_type)

        self.files = formatted_files
        return self

    def __str__(self) -> str:
        """
        Return a string representation of the Request object.

        :return: A string representation of the Request object.
        :rtype: str
        """
        return f"Request(url={self.url}, method={self.method}, headers={self.headers}, body={self.body})"
