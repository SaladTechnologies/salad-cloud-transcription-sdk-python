# Salad Cloud Transcription SDK for Python

A Python SDK for interacting with the Salad Cloud Transcription service, which provides speech-to-text capabilities.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Sample Usage](#sample-usage)
  - [Start a Transcription Job and Wait for Completion](#start-a-transcription-job-and-wait-for-completion)
  - [Start a Transcription Job and Poll for Status](#start-a-transcription-job-and-poll-for-status)
  - [Start a Transcription Job and Get Updates via Webhook](#start-a-transcription-job-and-get-updates-via-webhook)
- [Development and Testing](#development-and-testing)
- [License](#license)
- [Support](#support)

## Installation

Install the package using pip:

```bash
pip install salad-cloud-transcription
```

## Quick Start

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk

# Initialize the SDK
sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

# Transcribe an audio file
result = sdk.transcription_client.transcribe(
    "path/to/audio.mp3",
    auto_poll = True)

# Print the transcription
print(result.text)
```

## Authentication

### API Key Authentication

The Salad Cloud Transcription API uses API keys as a form of authentication. An API key is a unique identifier used to authenticate a user, developer, or a program that is calling the API.

### Setting the API Key

When you initialize the SDK, you can set the API key as follows:

```python
sdk = SaladCloudTranscriptionSdk(api_key="YOUR_API_KEY")
```

If you need to set or update the API key after initializing the SDK, you can use:

```python
sdk.set_api_key("YOUR_API_KEY")
```

## Sample Usage

### Start a Transcription Job and wait for it to complete

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk

# Initialize the SDK
sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

# Start a transcription job and wait for the result
# When the job is processed, this function returns a InferenceEndpointJob
result = sdk.transcription_client.transcribe(
    "path/to/audio.mp3",
    auto_poll = True)

# The output property of the InferenceEndpointJob is a either a TranscriptionJobFileOutput 
# or a TranscriptionJobOutput. You can print it to examine job results.
print(result.output)
```

### Start a Transcription Job and poll for status

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk

# Initialize the SDK
sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

# Start a transcription job. auto_poll = False
job = sdk.transcription_client.start_transcription_job("path/to/audio.mp3")

# Poll for the job status
while True:
    job = self._get_transcription_job_internal(organization_name, job.id_)
    if job.status in [
        Status.SUCCEEDED.value,
        Status.FAILED.value,
        Status.CANCELLED.value,
        ]:
        break
    time.sleep(5)

if job.status == Status.SUCCEEDED.value:
    print(job.output)
```

### Start a Transcription Job and Get Updates via a Webhook

First, initialize a transcription job.

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk

# Initialize the SDK
sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

# Start a transcription job with a webhook URL
job = sdk.transcription_client.start_transcription_job(
    "path/to/audio.mp3",
    webhook_url="https://your-webhook-endpoint.com"
)

print(f"Job started with ID: {job.id}")
```

In your webhook handler you need to validate the payload being sent to you:

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk

def webhook_handler(request):
    # Initialize the SDK
    sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

    # Extract the signing parameters from the request headers
    payload = request.json()  
    webhook_signature = request.headers.get("webhook-signature")
    webhook_timestamp = request.headers.get("webhook-timestamp")
    webhook_message_id = request.headers.get("webhook-id")
 
    # Retrieve the webhook signing secret for your Salad organization
    sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")
    secret_key_service = sdk.webhook_secret_key
    secret_key_response = secret_key_service.get_webhook_secret_key(
        "your_organization_name")

    signing_secret = f"whsec_{secret_key_response.secret_key}"

    # Process the webhook payload
    var job = sdk.transcription_client.process_webhook_request(
        payload=payload,
        signing_secret = signing_secret,
        webhook_id=webhook_message_id,
        webhook_timestamp=webhook_timestamp,
        webhook_signature=webhook_signature,
    )

    # The payload verification result is a TranscriptionWebhookPayload. 
    # Its data field is a InferenceEndpointJob and it contains the transcription job output.
    print(job.data)
```

## License

This SDK is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please email support@salad.com or visit our documentation at https://docs.salad.com.
