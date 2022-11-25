from tabulate import tabulate
from slack.errors import SlackApiError
import sys
import logging
import slack
import requests
import json
from datetime import date
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

class Slackalert:
    """To send cost report on slack."""
    def __init__(self, channel=None, webhook_url=None):
        self.channel = channel
        self.webhook_url = webhook_url
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def get_resource_list(self, resource_name, resource_info, resource_header, resource_list, resource_savings):
        """Returns all the idle resource information in a dictionary format."""
        resource_list.insert(0, resource_header)
        resource_info[resource_name] = {}
        resource_info[resource_name]['Resources'] = resource_list
        resource_info[resource_name]['Savings'] = resource_savings
        return resource_info

    def slack_alert(self, resource_info, account_name, total_savings,bucket_name,current_datetime,reporting_platform):
        try:   
            date_obj = date.today()
            date_obj_format = date_obj.strftime("%d %b %Y")
            s3_signature ={
                    'v4':'s3v4',
                    'v2':'s3'
                    }
            session = boto3.Session(profile_name='test-1')
            
            s3Client = session.client("s3",
                                    config=Config(signature_version=s3_signature['v4'])
                                    )
            
            print("b"+bucket_name)
            response = s3Client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': current_datetime+"/pennypincher_findings.html"},
                                                    ExpiresIn=86400)
            #print(response)
            print("total saving is"+total_savings)
            #list to store fields
            field = []
            for res in resource_info:
                key = {
					"type": "plain_text",
					"text": res,
		        }
                field.append(key)
                val = {
                "type": "plain_text",
                "text": "$"+str(resource_info[res]['Savings']),
                }
                field.append(val)
            total_saving={
                        "type": "plain_text",
                        "text": "Total Monthly Savings",
            }
            amount ={
                        "type": "plain_text",
                        "text": "$"+total_savings,
            }
            field.append(total_saving)
            field.append(amount)
            
            if 'slack' and 's3' in reporting_platform:
                reportDetails={
                        "type": "plain_text",
                        "text": "Check detail report here: "
                }
                bucket={
                        "type": "mrkdwn",
                        "text": "<"+response +"|"+ bucket_name +">"
                }
                note={
                        "type": "plain_text",
                        "text": "Note: Above URL is valid for 24 hours"
                }
                field.append(reportDetails)
                field.append(bucket)
                field.append(note)
            else:
                s3_note={
                        "type": "plain_text",
                        "text": "To check the detailed report enable s3",
                        }
                field.append(s3_note)
            
            #message to send in slack
            slack_msg = {
                            "attachments": [
                            {
                                "blocks": [
                                {
                                    "type": "section",
                                    "text": {
                                                "type": "plain_text",
                                                "text": "Pennypincher - "+str(date_obj_format)+" - Savings Report",
                                            }
                                },
                                {
                                    "type": "section",
                                    "fields": field
                                }
                                ]
                            }
                            ]
                        }
            #posting message into slack channel
            requests.post(self.webhook_url,data=json.dumps(slack_msg))
            print("Sending the Cost Optimization report to slack "+ self.channel)
            
        except Exception as e:
            self.logger.error(
                "Error on line {} in slack_send.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)
            
            
#"2022-11-21T07-44/pennypincher_findings.html"


        
            
        
        
