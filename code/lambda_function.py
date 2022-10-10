import os
import logging
import sys
from utils.html_functions import HTML
from utils.ses import SES
from aws.resources import Resources
from utils.slack_send import Slackalert
from utils.config import config
def lambda_handler(event=None, context=None):
  
    config = os.getenv('config', 'Null')                       
    
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
        ses_obj = SES()    #Object to send email
        slack_obj = Slackalert()           #object to send report to slack

        html, resource_info, total_savings = resource.get_report(html_obj, slack_obj)
        print("Total savings: $" + str(round(total_savings, 2)))
        
        if config.reporting_platform.lower() == 'email':
            ses_obj.ses_sendmail(
                sub='Cost Optimization Report | ' + config.account_name + ' | Total Savings: $'+ str(round(total_savings, 2)),
                html=html)
        elif config.reporting_platform.lower() == 'slack':
            slack_obj.slack_alert(resource_info, config.account_name, str(round(total_savings, 2)))
        elif config.reporting_platform.lower() == 'email and slack':
            ses_obj.ses_sendmail(
                sub='Cost Optimization Report | ' + config.account_name + ' | Total Savings: $' + str(round(total_savings, 2)),
                html=html)
            slack_obj.slack_alert(resource_info, config.account_name, str(round(total_savings, 2)))
        else:
            header = '<h3><b>Cost Optimization Report |  ' + config.account_name + ' | Total Savings: $'+ str(round(total_savings, 2)) + '</h3></b>'
            html = header + html
            path = os.getcwd()+ '/findings.html'
            f = open(path, "w+")
            f.write(html)
            f.close
            print("Findings file is at: findings.html")

    except Exception as e:
        logger.error("Error on line {} in lambda_function.py".format(sys.exc_info()[-1].tb_lineno) +
                     " | Message: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    lambda_handler()