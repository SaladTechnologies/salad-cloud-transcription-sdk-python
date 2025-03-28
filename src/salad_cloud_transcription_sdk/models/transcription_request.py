from __future__ import annotations
from typing import Dict, Any, Optional
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .transcription_job_input import TranscriptionJobInput


@JsonMap({"options": "input"})
class TranscriptionRequest(BaseModel):
    """A request to create a transcription job

    :param options: Configuration settings for the transcription job
    :type options: TranscriptionJobInput
    :param webhook: URL to receive transcription completion callback (optional)
    :type webhook: Optional[str]
    :param metadata: Additional metadata to associate with the transcription job (optional)
    :type metadata: Optional[Dict[str, Any]]
    """

    def __init__(
        self,
        options: TranscriptionJobInput,
        webhook: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.options = self._define_object(options, TranscriptionJobInput)
        self.webhook = (
            self._define_str("webhook", webhook) if webhook is not None else None
        )
        self.metadata = metadata if metadata is not None else {}
        self._kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TranscriptionRequest to a dictionary

        :return: Dictionary representation of this instance
        :rtype: Dict[str, Any]
        """
        result = {"input": self.options.to_dict()}

        if self.webhook is not None:
            result["webhook"] = self.webhook

        if self.metadata:
            result["metadata"] = self.metadata

        return result
