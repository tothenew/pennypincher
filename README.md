## Penny Pincher - An alerting solution for Cloud Cost Optimization

### Aim 

Penny Pincher is a tool that identifies all the resources which are provisioned but are not being used i.e. are idle and notifies you about the potential savings over email and slack.

### Features

1. Generates a report consisting of all the idle resources in the account and potential savings.
2. Two platforms are supported for receiving the report, one is email and another is slack.
3. The number of days for which resource metrics (usage) is to be monitored can be set by the end user.
4. The solution is easily deployable as the whole setup can be done using AWS Cloudformation or Docker.

### Pre-requisites

1. The IAM user used for the setup should have access to AWS S3, AWS IAM, AWS Lambda, AWS SES and AWS Cloudformation.
 * You can also use this custom [policy](docs/policy.json) to run Penny Pincher.
2. An AWS S3 bucket. (Only if the setup is to be done using Cloudformation)
3. A slack workspace. (Only if cost report is to be sent on any slack channel)
4. A verified SES email Address. (Only if cost report is to be sent over email)

## Quick Setup

### Docker

To start Penny Pincher, run the following command
```bash
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=AWS_REGION
```
```bash
docker-compose up --build
```
After the setup is complete, it will generate the report in an HTML page, **findings.html**.

![Alt](/images/main/sample_email_report.png)

For detailed instructions, refer to [Setup through Docker Compose](docs/setup_through_docker.md)

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


### FAQ
1. How can I deploy Penny Pincher to one's account?

The whole setup can be deployed either using [AWS Cloudformation](docs/setup_through_cloudformation.md) or [Docker](docs/setup_through_docker.md).

2. What are the alert methods supported by Penny Pincher?

It supports both the slack and the email for notifying the user with the report.

3. Can I use a custom CloudWatch metrics?

As of now, custom CloudWatch metrics are not supported, but, you can configure the [advance settings](docs/advanced_settings.md).


### Known Issues
1. In rare circumstances, there might be an issue in pricing when the Europiean regions are included. This is due to the response of the pricing API for the Europiean regions is in different format sometimes. 

### Features in Development
1. Working on supporting the data output in JSON format. This will allow for the additional output formats like xlsx and csv.
2. User's input is not enabled for configuring the recommendation criteria.