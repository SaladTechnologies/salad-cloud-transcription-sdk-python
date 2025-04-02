from enum import Enum
from typing import Dict, Any, Union
from datetime import datetime
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from salad_cloud_sdk.models import (
    InferenceEndpointJob,
)


class WebhookEventTypes(str, Enum):
    """All webhook event types."""

    INFERENCE_ENDPOINT_JOB_CANCELED = "inference_endpoint.job.canceled"
    """The event type for a canceled Inference Endpoint job."""

    INFERENCE_ENDPOINT_JOB_FAILED = "inference_endpoint.job.failed"
    """The event type for a failed Inference Endpoint job."""

    INFERENCE_ENDPOINT_JOB_SUCCEEDED = "inference_endpoint.job.succeeded"
    """The event type for a succeeded Inference Endpoint job."""

    QUEUE_JOB_CANCELED = "queue.job.canceled"
    """The event type for a canceled Queue job."""

    QUEUE_JOB_FAILED = "queue.job.failed"
    """The event type for a failed Queue job."""

    QUEUE_JOB_SUCCEEDED = "queue.job.succeeded"
    """The event type for a succeeded Queue job."""


@JsonMap({})
class TranscriptionWebhookPayload(BaseModel):
    """Information about a webhook payload from the transcription service

    :param type: The event type of the webhook
    :type type: WebhookEventTypes
    :param timestamp: The timestamp when the event was generated
    :type timestamp: datetime
    :param data: The transcription job data associated with the webhook
    :type data: InferenceEndpointJob
    """

    def __init__(
        self,
        type: str,
        timestamp: str,
        data: Dict[str, Any],
        **kwargs,
    ):
        self.type = self._define_str("type", type)
        self.timestamp = self._define_str("timestamp", timestamp)
        self.data = InferenceEndpointJob._unmap(data) if data else None
        self._kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TranscriptionWebhookPayload object to a dictionary

        :return: Dictionary representation of this instance
        :rtype: Dict[str, Any]
        """
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "data": self.data.to_dict() if self.data else {},
        }

    @classmethod
    def from_json(
        cls, json_data: Union[str, bytes, Dict[str, Any]]
    ) -> "TranscriptionWebhookPayload":
        """Creates a TranscriptionWebhookPayload instance from JSON data

        :param json_data: JSON string, bytes, or dictionary representation of TranscriptionWebhookPayload
        :type json_data: Union[str, bytes, Dict[str, Any]]
        :return: A new TranscriptionWebhookPayload instance
        :rtype: TranscriptionWebhookPayload
        """
        import json

        # Preprocess the JSON to rename 'type' to 'action' in 'data -> events'
        if isinstance(json_data, (str, bytes)):
            if isinstance(json_data, bytes):
                json_data = json_data.decode("utf-8")
            json_data = json.loads(json_data)

        if (
            isinstance(json_data, dict)
            and "data" in json_data
            and "events" in json_data["data"]
        ):
            for event in json_data["data"]["events"]:
                if isinstance(event, dict) and "type" in event:
                    event["action"] = event.pop("type")

        return cls(**json_data)
