from __future__ import annotations
from typing import Dict, Any, Union
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class TranscriptionJobFileOutput(BaseModel):
    """Information about transcription job output when return_as_file is set to True

    :param url: URL to the transcription output file
    :type url: str
    :param duration_in_seconds: Duration of the job in seconds
    :type duration_in_seconds: float
    :param duration: Processing duration
    :type duration: float
    :param processing_time: Time taken to process the transcription
    :type processing_time: float
    """

    def __init__(
        self,
        url: str,
        duration_in_seconds: float,
        duration: float,
        processing_time: float,
        **kwargs,
    ):
        self.url = self._define_str("url", url)
        self.duration_in_seconds = self._define_number(
            "duration_in_seconds", duration_in_seconds
        )
        self.duration = self._define_number("duration", duration)
        self.processing_time = self._define_number("processing_time", processing_time)
        self._kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TranscriptionJobFileOutput object to a dictionary

        :return: Dictionary representation of this instance
        :rtype: Dict[str, Any]
        """
        return {
            "url": self.url,
            "duration_in_seconds": self.duration_in_seconds,
            "duration": self.duration,
            "processing_time": self.processing_time,
        }

    @classmethod
    def from_json(
        cls, json_data: Union[str, bytes, Dict[str, Any]]
    ) -> TranscriptionJobFileOutput:
        """Creates a TranscriptionJobFileOutput instance from JSON data

        :param json_data: JSON string, bytes, or dictionary representation of TranscriptionJobFileOutput
        :type json_data: Union[str, bytes, Dict[str, Any]]
        :return: A new TranscriptionJobFileOutput instance
        :rtype: TranscriptionJobFileOutput
        """
        import json

        if isinstance(json_data, dict):
            data = json_data
        else:
            if isinstance(json_data, bytes):
                json_data = json_data.decode("utf-8")
            data = json.loads(json_data)

        return cls(**data)
