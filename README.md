# Twitch Polly

This is a small web service that proxies Amazon Polly TTS requests, with access control based on Twitch subs.

## Usage

First, set up [twitch-bot-auth](https://github.com/sugoidogo/twitch-bot-auth)
and an AWS account, with an access key for Amazon Polly.
I would also recommend installing `wheel` at this point if it isn't aleady.
Clone this repo, and run `pip install -r requirements.txt`.
A config file (`twitch-polly.ini`) will be generated and the script will exit.
After populating config values, you can run the script again to start the server.

## API

This server proxes the 2 API endpoints required for a TTS widget:

1. [/synthesize_speech](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly/client/synthesize_speech.html)
2. [/describe_voices](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly/client/describe_voices.html)

all polly options are accepted as query parameters.

## Config

```ini
[AWS]
# populate these values from your AWS account
aws_access_key_id = 
aws_secret_access_key = 
region_name = 

[network]
# These settings control the HTTP server binding
ip = localhost
# leave this on 0 to automatically select a port
port = 0

[twitch-bot-auth]
# This is the url to your twitch-bot-auth instance.
url = 
# The values below indicate teir 1, 2, and 3 subs respectively.
access-tier = 1000
ssml-tier = 2000
neural-tier = 3000
```

# Support
See [my profile](https://github.com/sugoidogo)