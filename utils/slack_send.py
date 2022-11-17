from tabulate import tabulate
from slack.errors import SlackApiError
import sys
import logging
import slack
import requests
import json
from datetime import date


class Slackalert:
    """To send cost report on slack."""
    def __init__(self, channel=None, slack_token=None, webhook=None):
        self.channel = channel
        self.slack_token = slack_token
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def get_resource_list(self, resource_name, resource_info, resource_header, resource_list, resource_savings):
        """Returns all the idle resource information in a dictionary format."""
        resource_list.insert(0, resource_header)
        resource_info[resource_name] = {}
        resource_info[resource_name]['Resources'] = resource_list
        resource_info[resource_name]['Savings'] = resource_savings
        return resource_info

    def slack_alert(self, resource_info, account_name, total_savings, webhook_url ):
        try:   
            date_obj = date.today()
            date_obj_format = date_obj.strftime("%d %b %Y")
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
                        "text": "Total Savings",
            }
            amount ={
                        "type": "plain_text",
                        "text": "$"+total_savings,
            }
            field.append(total_saving)
            field.append(amount)
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
            requests.post(webhook_url,data=json.dumps(slack_msg))
            
        except Exception as e:
            self.logger.error(
                "Error on line {} in slack_send.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)


        
            
        # try:
        #     client = slack.WebClient(token=self.slack_token)

        #     f = open("/tmp/cost_optimization_report.txt", "w+")

        #     for res in resource_info.keys():       
        #         #Converts resource info dictionary to tabular format.
        #         f.write('\n' + 'Resource: ' + res + '\n')
        #         resource_table = tabulate(resource_info[res]['Resources'][1:],
        #                                   headers=resource_info[res]['Resources'][0], tablefmt="grid",
        #                                   disable_numparse=True)
        #         f.write('\n' + resource_table + '\n \n' + 'Savings: $' + str(resource_info[res]['Savings']) + '\n')
        #     f.close()
        #     response = client.files_upload(
        #         file='/tmp/cost_optimization_report.txt',
        #         initial_comment='Cost Optimization Report | ' + account_name + ' | Total Savings: $' + str(total_savings),
        #         channels=self.channel
        #     )
            

        #     print("Sending the Cost Optimization report to slack "+ self.channel)
            
            
            
            
            

        # except SlackApiError as e:
        #     """You will get a SlackApiError if "ok" is False."""
        #     assert e.response["ok"] is False
        #     assert e.response["error"]  
        #     """str like 'invalid_auth', 'channel_not_found'."""
        #     self.logger.error("Slack api error: {e.response['error']} | Error in slack_send.py")
        #     sys.exit(1)

        
