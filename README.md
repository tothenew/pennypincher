## Penny Pincher - An alerting solution for Cloud Cost Optimization

//readme1
### Aim 

The aim is to setup a lambda function which sends information of all the resources which are provisioned but are not being used i.e. are idle along with potential savings over email and slack.

### Features

1. Generates a report consisting of all the idle resources in the account and potential savings.
2. Two platforms are supported for receiving the report, one is email and another is slack.
3. The number of days for which resource metrics (usage) is to be monitored can be set by the end user.
4. The solution is easily deployable as the whole setup is done using AWS Cloudformation.

### Pre-requisites

1. The IAM user used to setup the lambda should have access to AWS S3, AWS IAM, AWS Lambda, AWS SES and AWS Cloudformation.
2. An AWS S3 bucket.
3. A slack workspace. (Only if cost report is to be sent on any slack channel)
4. A verified SES email Adddress. (Only if cost report is to be sent over email)

### Quick Setup

To start Penny Pincher, run the following command
        ```
        docker-compose up
        ```

### Authentication
Before launching Penny Pincher you need to configure your AWS authentication method
AWS_PROFILES
ACCESS KEY

Refer to [here](docs/setup_through_cloudformation.md)  for a detailed setup
//setup on local- code block- run for docker

//readme 2-brief couple liner for setup(4 lines)-hyperlink for detailed setup readme

//README 3
### Advanced settings
Advanced configuration details can be found [here](docs/advanced_settings.md)


