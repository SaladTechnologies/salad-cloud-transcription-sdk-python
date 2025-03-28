import json
import pytest
from salad_cloud_sdk.models import InferenceEndpointJob
from salad_cloud_transcription_sdk.models.transcription_webhook_payload import (
    TranscriptionWebhookPayload,
)
from salad_cloud_transcription_sdk.services.utils.webhooks import (
    WebhookVerificationError,
)
from salad_cloud_sdk import SaladCloudSdk


def get_webhook_signing_secret(api_key, api_url, organization_name):
    """Retrieve the real webhook signing secret using the SDK"""
    sdk = SaladCloudSdk(api_key=api_key, base_url=api_url)
    secret_key_service = sdk.webhook_secret_key
    secret_key = secret_key_service.get_webhook_secret_key(organization_name)

    print(secret_key)
    return f"whsec_{secret_key.secret_key}"


@pytest.mark.skip(
    reason="Skipping this because it needs a recent payload. The timestamp is validated as well."
)
def test_process_webhook_request(transcription_service, webhook_data, test_config):
    """Test processing a webhook request with valid data"""

    payload = webhook_data
    webhook_id = "msg_TYEVGtKE5Swr21kS6Xh5WX"
    webhook_timestamp = "1743079715"
    webhook_signature = "v1,fKqKecmtbHc+zuUyFeSwuUXXU5rwu4P0sHc+o18o6no="

    signing_secret = get_webhook_signing_secret(
        api_key=test_config.API_KEY,
        api_url=test_config.API_URL,
        organization_name=test_config.ORGANIZATION_NAME,
    )

    result = transcription_service.process_webhook_request(
        payload=payload,
        signing_secret=signing_secret,
        webhook_id=webhook_id,
        webhook_timestamp=webhook_timestamp,
        webhook_signature=webhook_signature,
    )

    assert result is not None
    assert isinstance(result, TranscriptionWebhookPayload)
    assert result.data is not None
    assert isinstance(result.data, InferenceEndpointJob)


def test_process_webhook_when_timestamp_too_old(
    transcription_service, webhook_timestamp_too_old_data, test_config
):
    """Test processing a webhook request with a timestamp that is too old"""
    webhook_event = webhook_timestamp_too_old_data[0]

    payload = json.dumps(webhook_event["payload"])
    webhook_id = webhook_event["webhook_id"]
    webhook_timestamp = webhook_event["webhook_timestamp"]
    webhook_signature = webhook_event["webhook_signature"]

    signing_secret = get_webhook_signing_secret(
        api_key=test_config.API_KEY,
        api_url=test_config.API_URL,
        organization_name=test_config.ORGANIZATION_NAME,
    )

    with pytest.raises(WebhookVerificationError) as excinfo:
        transcription_service.process_webhook_request(
            payload=payload,
            signing_secret=signing_secret,
            webhook_id=webhook_id,
            webhook_timestamp=webhook_timestamp,
            webhook_signature=webhook_signature,
        )

    assert "Message timestamp too old" in str(excinfo.value)


def test_process_webhook_request_invalid_signature(
    transcription_service, webhook_data, test_config
):
    """Test processing a webhook request with invalid signature"""
    webhook_event = webhook_data[0]

    payload = json.dumps(webhook_event["payload"])
    webhook_id = webhook_event["webhook_id"]
    webhook_timestamp = webhook_event["webhook_timestamp"]
    webhook_signature = "v1,invalid_signature"

    signing_secret = get_webhook_signing_secret(
        api_key=test_config.API_KEY,
        api_url=test_config.API_URL,
        organization_name=test_config.ORGANIZATION_NAME,
    )

    with pytest.raises(WebhookVerificationError):
        transcription_service.process_webhook_request(
            payload=payload,
            signing_secret=signing_secret,
            webhook_id=webhook_id,
            webhook_timestamp=webhook_timestamp,
            webhook_signature=webhook_signature,
        )
