## Penny Pincher - Cloud Resource Optimization recommendation based on historical data to save cost.

[![CodeQL Status](https://github.com/tothenew/pennypincher/workflows/CodeQL/badge.svg)](https://github.com/tothenew/pennypincher/actions)
[![LICENSE](https://img.shields.io/github/license/tothenew/pennypincher)](https://github.com/tothenew/pennypincher/blob/master/LICENSE)
[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=&templateURL=https://penny-pincher-s3-bucket.s3.amazonaws.com/penny_pincher_cfn.yml)

### Overview 

Penny Pincher is a tool that identifies all the resources which are provisioned but are not being used i.e. are idle and notifies you about the potential savings over email and slack.


### Scope
The tool is created by considering three types of user 
1. Simple user - An end-to-end Cloudformation which will deploy the tool as a lambda function, 2.lambda invocation will generate the report and will be shared over slack, email, and S3.
2. Power-user - A docker run command which will allow users to generate the reports on their local machine
3. Dev user - The user can work as a developer by contributing to the repository.
### Features

1. Generates a report consisting of all the idle resources in the account and potential savings.
2. Three platforms; slack,email and S3 are supported for receiving the report.
3. HTML and csv reports are supported.
4. The end user can modify the default cloudwatch metric values using a configuration file with Global environment variable support.
5. The solution is easily deployable as the whole setup can be done using AWS Cloudformation, docker and local.
6. End user also recieve an inventory file in csv format of all the scanned resources, it helps in draw out the comparison and coverage of the tool/
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
 Boto3 API is used to scan supported the resources in the account, scanned result list out the idle resources based resource and cloudwatch metrics. Idle resource further run down our pricing matrix to genrete the reports in csv and html format. Report shows the potential cost saving amount for each resources. The end user can recieve report via slack or email and cab also store them in s3 buckets.

### Pre-requisites

1. To scan the entire account, the IAM user or keys should have ReadOnlyAccess.
2. Supported Python version v3 and above.
3. Supported Boto3 version v1.17.66 and above
4. S3 bucket - to store reports (If you want s3 as reporting platform)
5. User should create IAM role with policies which are listed below 
   > Note - Replace the 'ReportBucket' with name of s3 bucket which you have created already
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeImages",
        "ec2:DescribeInstances",
        "ec2:DescribeRegions",
        "ec2:DescribeVolumes",
        "ec2:DescribeAddresses",
        "pricing:GetProducts",
        "elasticache:DescribeCacheClusters",
        "es:ListDomainNames",
        "es:DescribeElasticsearchDomain",
        "elasticloadbalancing:DescribeLoadBalancers",
        "rds:DescribeDBInstances",
        "redshift:DescribeClusters",
        "ses:SendEmail",
        "logs:CreateLogStream",
        "logs:CreateLogGroup",
        "logs:PutLogEvents",
        "cloudwatch:GetMetricStatistics",
        "rds:DescribeOrderableDBInstanceOptions"
      ],
      "Resource": "*"
    },
    {
      "Sid": "VisualEditor1",
      "Effect": "Allow",
      "Action": "*",
      "Resource": "arn:aws:s3:::${ReportBucket}/*"
    }
  ]
}
```

### Permissions which needs to be give in IAM role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeImages",
        "ec2:DescribeInstances",
        "ec2:DescribeRegions",
        "ec2:DescribeVolumes",
        "ec2:DescribeAddresses",
        "pricing:GetProducts",
        "elasticache:DescribeCacheClusters",
        "es:ListDomainNames",
        "es:DescribeElasticsearchDomain",
        "elasticloadbalancing:DescribeLoadBalancers",
        "rds:DescribeDBInstances",
        "redshift:DescribeClusters",
        "ses:SendEmail",
        "logs:CreateLogStream",
        "logs:CreateLogGroup",
        "logs:PutLogEvents",
        "cloudwatch:GetMetricStatistics",
        "rds:DescribeOrderableDBInstanceOptions"
      ],
      "Resource": "*"
    },
    {
      "Sid": "VisualEditor1",
      "Effect": "Allow",
      "Action": "*",
      "Resource": "arn:aws:s3:::${ReportBucket}/*"
    }
  ]
}
```

### There are three ways to use this tool, which are as follows

### 1. With Cloudformation
1. At the top of this readme.md file there is one button named 'Launch Stack', click on this button.
2. Enter required information.
3. Launch cnf stack with 'submit' button.
### 2. Quick Setup With Docker


To start Penny Pincher, run the following command
```bash
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=AWS_REGION
```
```bash
docker-compose up --build
```
After the setup is complete, it will generate the report in an HTML and CSV format.
 

![Alt](/docs/images/main/sample_email_report.png)

For detailed instructions, refer to [Setup through Docker Compose](docs/setup_through_docker.md)

### 3. Local

1. Set up AWS CLI or Generate the access tokens and set them as environment variables.
2. `pip3 install -r requirements.txt`
3. `python3 main.py`

### If user choose 'email' as a reporting platform then how does user get an email notification ?

1. An email address which we are using as identity to send report, it needs to be verified before we use it. 
2. While deploying tool as lambda function through cloudformation stack, it verify an email and user gets one verification email in which user can find one link and he/she needs to follow that link to verify that email.
3. After verification user gets the reports on same email.
### Configuration Files and Usage
Pennnypincher finds the idle resources based on the default criteria mentioned in the below table.
We have provided support for [config.yaml](https://github.com/tothenew/pennypincher/blob/release_1.0/config.yaml) file which allows the end user to override the default configuration values.
Users just need to uncomment the resource and config block to change the default values.


### List of Global Environment variables

```
1. CHANNEL_NAME:- Slack Channel Name
2. WEBHOOK_URL:- Slack Channel Webhook URL (Ref: [Sending Message Using Incoming Webhooks](https://api.slack.com/messaging/webhooks))
3. FROM_ADDRESS* :- Sender Email Address
4. TO_ADDRESS* :- Receiver Email Address
5. SES_REGION
6. REPORTING_PLATFORM :- Where to send the report 
    1. email*
    2. slack
    3. s3
    4. Generate on Local (Default)
8. ACCOUNT_NAME :- AWS Account Name
```

`All of the above variables are Optional`

*Not Supported on Local
Advanced configuration details can be found [here](https://github.com/tothenew/pennypincher/blob/release_1.0/config.yaml)


### Recommendation Logic

The following table lists the criteria kept to decide if the resource is idle or not and mentions the recommendations which can help in cost saving. This is configurable via [config.yaml](https://github.com/tothenew/pennypincher/blob/release_1.0/config.yaml)


### FAQ

1. How can I deploy Penny Pincher to one's account?

    The whole setup can be deployed either using  [Docker](https://github.com/IntelliGrape/pennypincher/blob/master/docs/setup_through_docker.md) or Can be run on a Local Machine

2. What are the alert methods supported by Penny Pincher?

    It supports both slack and email for notifying the user of the report.

3. Can I use a custom CloudWatch metrics?

    As of now, custom CloudWatch metrics are not supported, but, you can configure the advanced [settings](https://github.com/tothenew/pennypincher/blob/release_1.0/config.yaml)

4. Can I override the condition criteria?

    Yes, it can be overridden via [config.yaml](https://github.com/tothenew/pennypincher/blob/release_1.0/config.yaml)

5. Potential Cost saving is calculated monthly or Yearly

    Monthly

6. Can I get the report in CSV format
    Yes, the Tool generates findings in HTML format as well as dumps the data in CSV format in the pennypincher_csv_report folder datetime-wise.

### Known Issues
1. The European region's response to AWS API is not consistent with other regions. So European regions cause unexpected issues sometimes.

### Features Releasing in 1.0
1. End-to-end Cloudformation run which can send reports to s3, slack, and email.
2. Functionality to configure Cloudwatatch and resource metric via config files.
3. Global environment variable support
4. A csv inventory of whole account for comparison and tool coverage.

### Future scope
1. Cron suppport in clouydformation.
2. Intellegent trend analysis on shared reports.
