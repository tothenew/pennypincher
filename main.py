import os
import logging
import sys
from datetime import datetime
from utils.html_functions import HTML
from utils.ses import SES
from utils.generate_csv import GENCSV
from aws.resources import Resources
from utils.slack_send import Slackalert
from utils.config_parser import parse_config
from utils.config_parser import merges
from utils.config_parser import check_env
def lambda_handler(event=None, context=None):
    print("Starting PennyPincher")

    default_config = parse_config('./utils/default.yaml') 
    overwrite_config = parse_config('./config.yaml') 
    final_config = merges(default_config,overwrite_config)
    resource_config = final_config['resources']
    env_config = final_config['config']['env']
    env_config = check_env(env_config)
    # print(f"Printing Resource config: {resource_config}")
    print(f"Printing env config: {env_config}")
    channel_name =  env_config['channel_name']   #Slack Channel Name
    slack_token = env_config['slack_token']                  #Slack Channel Token
    config = env_config['config']                         #Configuration for Cloudwatch e.g. ebs=20, lb=15
    from_address = env_config['from_address']               #SES verified email address from which email is to be sent
    to_address = env_config['to_address']         #Email addresses of recipents (Comma Separated)
    ses_region = env_config['ses_region']                   #Region where SES is configured
    reporting_platform = env_config['reporting_platform']    #Email/Slack/Email and Slack
    account_name = env_config['account_name'] 
    #For removing any existing loggers in lambda
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    #Initilizaing logger for error logging
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger()
    try:
        resource = Resources(resource_config)    #Object for generating report
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
            path = os.getcwd()+ '/pennypincher_findings.html'
            f = open(path, "w+")
            f.write(html)
            f.close
            print("Findings File is at: pennypincher_findings.html")
            current_datetime=datetime.utcnow().isoformat("T","minutes").replace(":", "-")
            dir_path=f"{os.getcwd()}/pennypincher_csv_report/{current_datetime}"
            os.makedirs(dir_path,exist_ok=True)
            if len(resource_info) > 0:
                csv_obj = GENCSV(resource_info, total_savings, dir_path, current_datetime)
                csv_obj.generate_csv()
                print(f"CSV Report is at: {dir_path} directory")

    except Exception as e:
        logger.error("Error on line {} in main.py".format(sys.exc_info()[-1].tb_lineno) +
                     " | Message: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    lambda_handler()