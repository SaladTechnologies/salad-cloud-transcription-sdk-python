from __future__ import annotations
from typing import Dict, Any
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .transcription_job_input import TranscriptionJobInput


@JsonMap({"options": "input"})
class TranscriptionRequest(BaseModel):
    """A request to create a transcription job
    
    :param options: Configuration settings for the transcription job
    :type options: TranscriptionJobInput
    :param webhook: URL to receive transcription completion callback
    :type webhook: str
    :param metadata: Additional metadata to associate with the transcription job
    :type metadata: Dict[str, Any]
    """
    
    def __init__(
        self,
        options: TranscriptionJobInput,
        webhook: str,
        metadata: Dict[str, Any],
        **kwargs
    ):
        self.options = self._define_object(options, TranscriptionJobInput)
        self.webhook = self._define_str("webhook", webhook)
        self.metadata = metadata
        self._kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TranscriptionRequest to a dictionary
        
        :return: Dictionary representation of this instance
        :rtype: Dict[str, Any]
        """
        return {
            "input": self.options.to_dict(),
            "webhook": self.webhook,
            "metadata": self.metadata
        }