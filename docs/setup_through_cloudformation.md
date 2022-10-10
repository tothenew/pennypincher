### Setup

1. Create an S3 bucket and upload the file code.zip and packages.zip in it. The code.zip and packages.zip file must be uploaded in the root directory of the S3 bucket. Steps for S3 bucket creation can be found [here](docs/s3_creation.md).
2. The report can be received either over email or over slack or both.
3. Create a slack channel, slack app and an OAuth token for that app. (This step can be skipped if report is to be sent only over email). Steps for slack app creation can be found [here](docs/slack_app_creation.md).
4. Verify an email address on AWS SES (Simple Email Service). The report will be received from this email id.(This step can be skipped if report is to be received only over slack) Steps for SES email verification can be found [here](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-email-addresses-procedure.html).
Note: Both email and slack can be selected as reporting platforms. However, selecting one platform either Email or Slack is necessary.

5. Search for Cloudformation in the AWS Console search bar and click on Cloudformation. 

![Alt](/docs/images/main/navigate_to_cloudformation_5.png)

6. On the Cloudformation console, click on **Create Stack**. 

![Alt](/docs/images/main/cloudformation_create_stack_6.png)

7. Select the **Template is ready** option in Prerequisite-Prepare template, select Template source as Upload a template file and Click on **Choose file**.

![Alt](/docs/images/main/cloudformation_choose_template_file_7.png)

8. Upload the penny_pincher_cfn.yml file and click on **Next**.

![Alt](/docs/images/main/upload_template_click_next_8.png)

9. Give a name to the stack. 

![Alt](/docs/images/main/stack_name_9.png)

10. Fill the parameters and Click on **Next**. The parameters are as follows: 
    * **AccountName**: Takes Account name as input.
    * **CloudwatchConfig**: For a basic setup, keep the default setting i.e. Null
    * **Reporting Platform**: Takes input in a dropdown format. Select "Email" if you want report only over email. Select "Slack" if you want report only over slack. Select "Email and Slack" if you want report over both.
    * **S3BucketName**: Give the name of the S3 bucket which contains code.zip and packages.zip.

    The SES related parameters are to be given if you want to receive report over email.

    * **SESFromEmailAddress**: Give an SES verified email address from which email containing the report will be sent.
    * **SESRegion**: Give the AWS region abbreviation in which SES email is verified.
    * **SESToEmailAddress**: Give the email ids on which email containing the report will be sent.

    The slack related parameters are to be given if you want to receive report on your slack channel.

    * **SlackChannelName**: Give the name of the slack channel on which report is to be sent.
    * **SlackToken**: Give the OAuth token for your Slack App.

![Alt](/docs/images/main/parameters_10.png)

11. In the Configure Stack Options page, leave everything as defaults and click on **Next**.

![Alt](/docs/images/main/configure_stack_options_11.png)

12. In the Review page, recheck the values of the parameters, scroll down to the end of the page, check the checkbox which says "I acknowledge that AWS CloudFormation might create IAM resources with custom names" and click on **Create stack** .

![Alt](/docs/images/main/final_create_stack_12.png)

13. On completion of the creation the stack screen would look as follows.

![Alt](/docs/images/main/creation_complete_13.png)

14. Search for Lambda in AWS Console search bar and click on Lambda.

![Alt](/docs/images/main/search_for_lambda_14.png)

15. On the Lambda console, it can be seen that a lambda named "Penny-Pincher" has been created. Click on the lambda "Penny-Pincher" .

![Alt](/docs/images/main/penny_pincher_lambda_created_15.png)

16. Click on **Test** button to run the Lambda .

![Alt](/docs/images/main/testing_the_lambda_16.png)

17. After a few minutes, the report will be generated and sent to your email id and/or slack channel in the following format.

    * Sample report on Email
    ![Alt](/docs/images/main/sample_email_report.png)

    * Sample report on Slack (A full view can be seen by clicking on the encircled button)
    ![Alt](/docs/images/main/sample_slack_report.png)