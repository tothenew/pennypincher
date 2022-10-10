import os

channel_name = os.getenv('channel_name', '-')                #Slack Channel Name
slack_token = os.getenv('slack_token', '-')                  #Slack Channel Token
config = os.getenv('config', 'Null')                            #Configuration for Cloudwatch e.g. ebs=20, lb=15
from_address = os.getenv('from_address','-')                #SES verified email address from which email is to be sent
to_address = os.getenv('to_address', '-').split(",")         #Email addresses of recipents (Comma Separated)
ses_region = os.getenv('ses_region', '-')                    #Region where SES is configured
reporting_platform = os.getenv('reporting_platform', '-')    #Email/Slack/Email and Slack
account_name = os.getenv('account_name', 'AWS Account')                #Account Name for which report is generated
