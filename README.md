## Penny Pincher - Cloud Resource Optimization recommendation based on historical data to save cost.

### Aim 

Penny Pincher is a tool that identifies all the resources which are provisioned but are not being used i.e. are idle and notifies you about the potential savings over email and slack.

### Features

1. Generates a report consisting of all the idle resources in the account and potential savings.
2. Two platforms are supported for receiving the report, one is email and another is slack.
3. The number of days for which resource metrics (usage) is to be monitored can be set by the end user.
4. The solution is easily deployable as the whole setup can be done using AWS Cloudformation or Docker.

### Supported Services & Regions
 The tool crawls all the regions to get the findings for the supported services 
    1. EBS
    2. EC2
    3. EIP
    4. Elasticache
    5. Elasticsearch
    6. Loadbalancer
    7. RDS


### How does it work?
 Boto3 API is used to scan the resources in the account according to the criteria defined in the configuration file and generate a report. 


### Pre-requisites

1. To scan the entire account, the IAM user or keys should have ReadOnlyAccess.
2. Supported Python version v3 and above.
3. Supported Boto3 version v1.17.66 and above


### Quick Setup With Docker


To start Penny Pincher, run the following command
```bash
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=AWS_REGION
export AWS_DEFAULT_REGION
```
```bash
docker-compose up --build
```
After the setup is complete, it will generate the report in an HTML and CSV format.
 

![Alt](/docs/images/main/sample_email_report.png)

For detailed instructions, refer to [Setup through Docker Compose](docs/setup_through_docker.md)

### Local

1. Set up AWS CLI or Generate the access tokens and set them as environment variables.
2. pip3 install -r requirements.txt
3. python3 main.py


### Configuration Files and Usage
Pennnypincher finds the idle resources based on the default criteria mentioned in the below table.
We have provided support for [config.yaml](https://github.com/tothenew/pennypincher/blob/release_1.0/config.yaml) file which allows the end user to override the default configuration values.
Users just need to uncomment the resource and config block to change the default values.


### Recommendation Logic

The following table lists the criteria kept to decide if the resource is idle or not and mentions the recommendations which can help in cost saving.

![Alt](/docs/images/main/recommendation_criteria.png)


### FAQ
1. How can I deploy Penny Pincher to one's account?

The whole setup can be deployed either using [AWS Cloudformation](docs/setup_through_cloudformation.md) or [Docker](docs/setup_through_docker.md).

2. What are the alert methods supported by Penny Pincher?

It supports both the slack and the email for notifying the user with the report.

3. Can I use a custom CloudWatch metrics?

As of now, custom CloudWatch metrics are not supported, but, you can configure the [advance settings](docs/advanced_settings.md).


### Known Issues
1. The European regions response for AWS API is not consistent with other regions. So European regions cause unexpected issues sometimes.

### Features in Development
1. Working on supporting the data output in JSON format. This will allow for the additional output formats like xlsx and csv.
2. User's input is not enabled for configuring the recommendation criteria.