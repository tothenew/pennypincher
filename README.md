## Penny Pincher - An alerting solution for Cloud Cost Optimization

### Aim 

Penny Pincher is a tool that identifies all the resources which are provisioned but are not being used i.e. are idle and notifies you about the potential savings over email and slack.

### Features

1. Generates a report consisting of all the idle resources in the account and potential savings.
2. Two platforms are supported for receiving the report, one is email and another is slack.
3. The number of days for which resource metrics (usage) is to be monitored can be set by the end user.
4. The solution is easily deployable as the whole setup can be done using AWS Cloudformation or Docker.

### Pre-requisites

1. The IAM user used to setup the lambda should have access to AWS S3, AWS IAM, AWS Lambda, AWS SES and AWS Cloudformation.
2. An AWS S3 bucket.
3. A slack workspace. (Only if cost report is to be sent on any slack channel)
4. A verified SES email Address. (Only if cost report is to be sent over email)

## Quick Setup

### Docker

To start Penny Pincher, run the following command
```bash
docker-compose up
```
It will generate a report in an HTML page, findings.html

#### Authentication
Before launching Penny Pincher, you need to configure your AWS authentication method in the `.env` file
```bash
AWS_ACCESS_KEY_ID=aws_access_key
AWS_SECRET_ACCESS_KEY=aws_secret_Access_key
```
### Cloudformation
1. Create an S3 bucket and upload the files code.zip and packages.zip in the bucket.
2. Create a cloudformation stack using the penny_pincher_cfn.yml template file.
3. Input the required parameters for receiving the report and create the stack
4. Go to the AWS Lambda console, select the lambda "Penny-Pincher". Click on Test button to    run the Lambda .
5. After a few minutes, you will receive the report on your email id and/or slack channel. 

For detailed instructions, refer to [Setup through Cloudformation](docs/setup_through_cloudformation.md)


### Advanced settings
Advanced configuration details can be found [here](docs/advanced_settings.md)

### Recommendation Logic

The following table lists the criteria kept to decide if the resource is idle or not and mentions the recommendations which can help in cost saving.

![Alt](/images/main/recommendation_criteria.png)

