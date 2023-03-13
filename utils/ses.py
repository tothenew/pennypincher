import boto3
import logging
from botocore import exceptions
import sys
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import os


class SES:
    """To send cost report using email."""
    def __init__(self, from_address=None, to_address=None, ses_region=None):
        self.from_address = from_address
        self.to_address = to_address
        self.ses_region = ses_region
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()
        
    def generate_summary_html(self, tl_saving, resource_info, reporting_platform, date, presigned_url, bucket_name):
        html_prefix = f""" <html>
                            <head>
                            <style>
                                table, th, td {{
                                border: 1px solid black;
                                border-collapse: collapse;
                                padding: 5px 15px;
                                vertical-align: middle;
                                text-align: left
                                }}
                                h7, td {{
                                padding: 5px 15px 5px 0;
                                }}
                                </style>
                            </head>
                            <body>
                            <h4>Pennypincher - {date} Savings Report</h4>
                            <table>"""

        html_suffix = " "
        res_list = []
        saving = []
        for res in resource_info:
            res_list.append(res)
            saving.append(f"${resource_info[res]['Savings']}")
        
        res_list.append("Total Monthly Savings")
        saving.append(f"${tl_saving}")

        if "s3" in reporting_platform:
            res_list.append("Check detail report here:")
            saving.append(f'<a href = "{presigned_url}">{bucket_name}</a>')
            html_suffix = "</table><h7><br>Note: Above URL is valid for 1 week</h7></body></html>"
        else:
            html_suffix = "</table><h7><br>Note: To check the detailed report enable s3</h7></body></html>"
        msg = {}
        for i,j in zip(res_list,saving):
            msg[i] = j
                        
        html = "<tr>"
        for key, value in msg.items():
            html = html + "<td>%s</td>" % (key) + "<td>%s</td>" % (value)+ "</tr><tr>"
        
        final_msg = ''
        final_msg = html_prefix + html + html_suffix
        
        return final_msg

    def ses_sendmail(self, sub, dir_path, tl_saving, resource_info, platform, current_date, url, bucket_name):   
        """Sends email."""
        
        # try:
        ses = boto3.client('ses', region_name='us-east-1')
        message = MIMEMultipart()
        message['Subject'] = sub
        message['From'] = self.from_address
    
        html = self.generate_summary_html(tl_saving, resource_info, platform, current_date, url, bucket_name)
        
        part = MIMEText(html, 'html')
        message.attach(part)
    
        files = [f'{dir_path}/pennypincher_summary_report.csv', f'{dir_path}/pennypincher_inventory.csv']
        
        for file in files:
            with open(file, 'rb') as f:
                part = MIMEApplication(f.read())
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
                message.attach(part)

        ses.send_raw_email(
        Source=message['From'],
        Destinations= self.to_address.split(','),
        RawMessage={
            'Data': message.as_string()
        }
        )
    
        print("Sending the Cost Optimization report to "+ self.to_address)        
        # except ses.meta.client.exceptions.MessageRejected as ex:
        #     if ex.response['Error']['Message'] == 'MessageRejected':
        #         self.logger.warning('email not verified')
        #         print(ex.response['Error']['Message'])
            
        # except exceptions.ClientError as error:
        #     if error.response['Error']['Code'] == 'LimitExceededException':
        #         self.logger.warning('API call limit exceeded; backing off and retrying...')
        #     else:
        #         self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
        #                           ' | Line {} in ses.py'.format(sys.exc_info()[-1].tb_lineno))
        #         sys.exit(1)

        # except Exception as e:
        #     self.logger.error("Error on line {} in ses.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
        #     sys.exit(1)
        
        