## Authentication
To start Penny Pincher, run the following commands
```bash
export AWS_ACCESS_KEY_ID     = YOUR_AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY = YOUR_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION    = AWS_REGION
```
If you are using AWS STS credentials, 
```bash
export AWS_SESSION_TOKEN     = YOUR_AWS_SESSION_TOKEN
```

## Starting Penny Pincher
```bash
docker-compose up --build
```
For all the consecutive runs, you can use the command
```bash
docker-compose up 
```

## Other Configuration

You can edit the [docker-compose.yml] file to provide more configuration details like-
    
```bash
    environment:  
      - AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY
      - AWS_DEFAULT_REGION
      - AWS_SESSION_TOKEN
      - config=Null
      - account_name=account_name
      - channel_name=channel_name
      - slack_token=slack_token
      - reporting_platform=reporting_platform
      - ses_region=ses_region
      - to_address=to_address
```