from dataclasses import dataclass
from typing import Optional, Dict, Any

from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class FileOperationResponse(BaseModel):
    """This class represents the response from a file sign or upload request."""

    def __init__(self, url: str, **kwargs):
        """Initialize a FileOperationResponse object

        :param url: The URL where the uploaded file can be accessed
        :type url: str
        """
        self.url = self._define_str("url", url)
        self._kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Converts the FileOperationResponse object to a dictionary

        :return: Dictionary representation of this instance
        :rtype: Dict[str, Any]
        """
        return {"url": self.url}
