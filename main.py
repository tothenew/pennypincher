import os
import logging
import cfnresponse
import sys
import boto3
import argparse
import uuid
from datetime import datetime
from utils.html_functions import HTML
from utils.ses import SES
from utils.generate_csv import GENCSV
from aws.resources import Resources
from utils.slack_send import Slackalert
from utils.config_parser import parse_config
from utils.config_parser import merges
from utils.config_parser import check_env
from utils.s3_send import uploadDirectory
from utils.filemanager import FileManager
from utils.generate_inv import GENINV
from utils.ses_verification import verify_identity
from botocore.client import Config
from datetime import date

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def lambda_handler(event=None, context=None):
    print("Starting PennyPincher")
    default_config = parse_config('./utils/default.yaml') 
    overwrite_config = parse_config('./config.yaml') 
    final_config = merges(default_config,overwrite_config)
    resource_config = final_config['resources']
    env_config = final_config['config']['env']
    env_config = check_env(env_config)
    channel_name =  env_config['channel_name']   #Slack Channel Name
    from_address = env_config['from_address']               #SES verified email address from which email is to be sent
    to_address = env_config['to_address']         #Email addresses of recipents (Comma Separated)
    ses_region = env_config['ses_region']                   #Region where SES is configured
    reporting_platform = env_config['reporting_platform']    #Email/Slack/Email and Slack
    account_name = env_config['account_name'] 
    webhook_url = env_config['webhook_url']
    report_bucket = env_config['report_bucket']
    
    #Verifying Identities
    if 'email' in  reporting_platform.lower().split(','):
        email_addresses = to_address.split(',')
        email_addresses.append(from_address)
        unique_list = set(email_addresses) 
        email_addresses = (list(unique_list))
        response= verify_identity(email_addresses)
        print(response)
    #Report Headerse
    headers_inventory = ['ResourceID','ResouceName','ServiceName','Type','VPC',
                          'State','Region', 'Idle'
                        ]
    headers = ['ResourceID','ResouceName','ServiceName','Type','VPC',
               'State','Region','Finding','EvaluationPeriod (seconds)','Criteria','Saving($)'
              ]

    #For removing any existing loggers in lambda
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    #Initilizaing logger for error logging
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger()
    current_dir = os.getcwd()

    try:
        print(reporting_platform.lower().split(','))
        resource = Resources(resource_config, headers, headers_inventory)    #Object for generating report
        html_obj = HTML()               #Object for generating html page
        ses_obj = SES(from_address=from_address, to_address=to_address, ses_region=ses_region)    #Object to send email
        slack_obj = Slackalert(channel=channel_name, webhook_url=webhook_url)           #object to send report to slack
        print(html_obj)
        
        # options to include and exclude aws resources while scanning the account
        parser = argparse.ArgumentParser()
        parser.add_argument("--include", type=str, help="resources which need to be scanned")
        parser.add_argument("--exclude", type=str, help="resources which need to be exclude from the scanning")
        args = parser.parse_args()
        resources_tobe_scanned = ['ec2', 'rds', 'l.b', 'ebs', 'eip', 'ec', 'es', 'redshift']
        if args.include:
            res = str(args.include)
            resources_tobe_scanned = res.lower().split(',')
        if args.exclude:
            res = str(args.exclude)
            excluded_res = res.lower().split(',')
            resources_tobe_scanned = [i for i in resources_tobe_scanned if i not in excluded_res]
            
        html, resource_info, total_savings, inventory_info = resource.get_report(html_obj, slack_obj, resources_tobe_scanned)
        print("Total savings: $" + str(round(total_savings, 2)))
        current_datetime=datetime.utcnow().isoformat("T","minutes").replace(":", "-")
        dir_path=f"/tmp/pennypincher_reports/{current_datetime}"
        os.makedirs(dir_path,exist_ok=True)
        date_obj = date.today()
        date_obj_format = date_obj.strftime("%d %b %Y")
        html_path = dir_path+ '/pennypincher_findings.html'
        header = '<h3><u><b>' + date_obj_format + ' Savings Report | Total Savings: $'+ str(round(total_savings, 2)) + '</b></u></h3>'
        logo = f'<img src="https://penny-pincher-s3-bucket.s3.amazonaws.com/pennypincher-logo.png" height="200" width="200" >'
        html = logo + header + html
        with FileManager(html_path, 'w') as f:
            f.write(html)
        print("Findings File is at: pennypincher_findings.html")
        file_name = "/tmp/pennypincher_reports"
        pre_url = ''
        if len(resource_info) > 0:
            csv_obj = GENCSV(resource_info, total_savings, dir_path, current_datetime)
            csv_obj.generate_csv()
            print(f"CSV Report is at: {dir_path} directory")
        if len(inventory_info) > 0 :
            inv_obj = GENINV(inventory_info, dir_path, current_datetime)
            inv_obj.generate_inv()
          ## Sending report in s3   
        if 's3' in  reporting_platform.lower().split(','):
            uploadDirectory(dir_path,report_bucket,current_datetime)
            s3_signature ={
                    'v4':'s3v4',
                    'v2':'s3'
                    }
            session = boto3.Session()  
            s3Client = session.client("s3",
                                    config=Config(signature_version=s3_signature['v4'])
                                    )
            pre_url = s3Client.generate_presigned_url('get_object',
                                                    Params={'Bucket': report_bucket,
                                                            'Key': current_datetime+"/pennypincher_findings.html"},
                                                    ExpiresIn=604800)
        if 'email' in  reporting_platform.lower().split(','):
            ses_obj.ses_sendmail(
                sub='Cost Optimization Report | ' + account_name + ' | Total Savings: $'+ str(round(total_savings, 2)), dir_path=dir_path,
                tl_saving = str(round(total_savings, 2)), resource_info = resource_info, platform= reporting_platform, current_date = date_obj_format, url=pre_url, bucket_name = report_bucket)
        if 'slack' in  reporting_platform.lower().split(','):
            print("Sending report to slack .....")
            slack_obj.slack_alert(resource_info, str(round(total_savings, 2)),report_bucket, date_obj_format, reporting_platform, pre_url)      
        return "Success"
    except Exception as e:
        logger.error("Error on line {} in main.py".format(sys.exc_info()[-1].tb_lineno) +
                     " | Message: " + str(e))
        return "Failed"


def cfnresponsefun(event, context):
    '''Redirect to handler func based on RequestType '''
    physical_resource_id = event.get('PhysicalResourceId', 'ssm-%s' % uuid.uuid4().hex)
    try:
        response = None
        print(f"Received event: {event}")
        if 'RequestType' in event:
            if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
                response = lambda_handler()
                print(response)
                if response == "Success":
                    cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Status': repr(response)}, physical_resource_id)
                else:
                    cfnresponse.send(event, context,cfnresponse.FAILED, {'Status': repr(response)}, physical_resource_id)
            elif event['RequestType'] == 'Delete':
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Status': repr(response)}, physical_resource_id)
        else:
            # When triggering lambda from UI or Cron
            response = lambda_handler()
            if response != "Success":
                return 0 #Failed
            else:
                return 'Completed Successfully'
    except Exception as ex:
        log.error("Error: Failed to %s trigger the lambda: %s" % (event['RequestType'], str(ex)))
        cfnresponse.send(event, context,
                        cfnresponse.FAILED,
                        {'Exception': repr(ex)})
        return 'Exception: %s' % str(ex)


if __name__ == "__main__":
    lambda_handler()
