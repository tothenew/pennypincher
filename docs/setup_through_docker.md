## Authentication
Configure your AWS credentials as environment variables.
```bash
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=AWS_REGION
```
If using AWS STS credentials, also set the value for session token.
```bash
export AWS_SESSION_TOKEN=YOUR_AWS_SESSION_TOKEN
```

## Starting Penny Pincher
To start Penny Pincher, run the following commands

```bash
docker-compose up --build
```
After the setup is complete, the results can be viewed in *findings.html*

For all the consecutive runs, you can use the command
```bash
docker-compose up 
```

## Other Configuration

You can update the environment variables in the [docker-compose.yml](../docker-compose.yml) file to provide more configuration details.

For example, if you wish to receive the findings report on slack, update the values of
channel_name, webhook_url and set reporting_platform = slack
    
```bash
    environment:  
      - AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY
      - AWS_DEFAULT_REGION
      - AWS_SESSION_TOKEN
      - config=Null
      - account_name=account_name
      - channel_name=channel_name
      - webhook_url=webhook_url
      - reporting_platform=reporting_platform
      - ses_region=ses_region
      - to_address=to_address
      - from_address=from_address
```
Advanced configuration details can be found [here](../docs/advanced_settings.md)