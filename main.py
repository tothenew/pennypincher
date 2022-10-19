import os
import logging
import sys
from utils.html_functions import HTML
from utils.ses import SES
from aws.resources import Resources
from utils.slack_send import Slackalert
def lambda_handler(event=None, context=None):
    channel_name = os.getenv('channel_name', '-')                #Slack Channel Name
    slack_token = os.getenv('slack_token', '-')                  #Slack Channel Token
    config = os.getenv('config', 'Null')                            #Configuration for Cloudwatch e.g. ebs=20, lb=15
    from_address = os.getenv('from_address','-')                #SES verified email address from which email is to be sent
    to_address = os.getenv('to_address', '-').split(",")         #Email addresses of recipents (Comma Separated)
    ses_region = os.getenv('ses_region', '-')                    #Region where SES is configured
    reporting_platform = os.getenv('reporting_platform', '-')    #Email/Slack/Email and Slack
    account_name = os.getenv('account_name', 'AWS Account')                #Account Name for which report is generated
    print("Starting PennyPincher")
    #For removing any existing loggers in lambda
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    #Initilizaing logger for error logging
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger()
    try:
        resource = Resources(config)    #Object for generating report
        html_obj = HTML()               #Object for generating html page
        ses_obj = SES(from_address=from_address, to_address=to_address, ses_region=ses_region)    #Object to send email
        slack_obj = Slackalert(channel=channel_name, slack_token=slack_token)           #object to send report to slack

        html, resource_info, total_savings = resource.get_report(html_obj, slack_obj)
        print("Total savings: $" + str(round(total_savings, 2)))
        
        if reporting_platform.lower() == 'email':
            ses_obj.ses_sendmail(
                sub='Cost Optimization Report | ' + account_name + ' | Total Savings: $'+ str(round(total_savings, 2)),
                html=html)
        elif reporting_platform.lower() == 'slack':
            slack_obj.slack_alert(resource_info, account_name, str(round(total_savings, 2)))
        elif reporting_platform.lower() == 'email and slack':
            ses_obj.ses_sendmail(
                sub='Cost Optimization Report | ' + account_name + ' | Total Savings: $' + str(round(total_savings, 2)),
                html=html)
            slack_obj.slack_alert(resource_info, account_name, str(round(total_savings, 2)))
        else:
            header = '<h3><b>Cost Optimization Report |  ' + account_name + ' | Total Savings: $'+ str(round(total_savings, 2)) + '</h3></b>'
            html = header + html
            path = os.getcwd()+ '/findings.html'
            f = open(path, "w+")
            f.write(html)
            f.close
            print("Findings file is at: findings.html")

    except Exception as e:
        logger.error("Error on line {} in main.py.py".format(sys.exc_info()[-1].tb_lineno) +
                     " | Message: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    lambda_handler()