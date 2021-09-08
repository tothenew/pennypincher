## Authentication
To start Penny Pincher, run the following commands
```bash
export AWS_ACCESS_KEY_ID     = YOUR_AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY = YOUR_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION    = AWS_REGION
```
If you are using AWS STS credentials, 
export AWS_SESSION_TOKEN     = YOUR_AWS_SESSION_TOKEN

## Starting Penny Pincher
```bash
docker-compose up --build
```
For all the consecutive runs, you can simply use the command
```bash
docker-compose up 
```

