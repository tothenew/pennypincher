### Advanced settings
For an advanced configuration, you can provide the following details-

* **account_name**: AWS account name.
* **config**: 
By default, Penny Pincher takes into account last 14 days usage of the resources. The number of days to be considered for generating the report can be mentioned specifically for each resource as follows-

   * In the CloudwatchConfig parameter while creating the cloudformation stack as follows:

   ![Alt](/docs/images/main/advanced_configuration.png)

   * In the [docker-compose.yml](../docker-compose.yml) file, the value of **config** can be   set in the format, *resource=number of days*. 
   For Example-
    ```bash
    config=ebs=20, lb=15
    ```
   For a basic setup, keep the default setting i.e. Null

* **reporting_platform**: Set the value to *"Email"* if you want report only over email. Set the value to *"Slack"* if you want report only over slack. Set the value to "Email and Slack" if you want report over both.

The *SES* related variables are to be given if you want to receive report over email.
*    **from_address** : Give an SES verified email address from which email containing the report will be sent.
*    **ses_region**: Give the AWS region abbreviation in which SES email is verified.
*    **to_address**: Give the email ids on which email containing the report will be sent.

The *Slack* related variables are to be given if you want to receive report on your slack channel.
*    **channel_name**: Give the name of the slack channel on which report is to be sent.
*    **webhook_url**: Give the webhook url of your slack channel.


### Architecture Diagram 

![Alt](/docs/images/main/penny_pincher_architecture_diagram.jpg)
