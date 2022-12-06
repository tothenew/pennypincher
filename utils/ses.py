import boto3
import logging
from botocore import exceptions
import sys


class SES:
    """To send cost report using email."""
    def __init__(self, from_address=None, to_address=None, ses_region=None):
        self.from_address = from_address
        self.to_address = to_address
        self.ses_region = ses_region
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def ses_sendmail(self, sub, html=''):   
        """Sends email."""
        
        try:
            self.to_address.split(',')
            ses = boto3.client('ses', region_name=self.ses_region)
            print(self.to_address)
            ses.send_email(
            Destination={
                "ToAddresses": self.to_address.split(','),
                'CcAddresses': [],
                'BccAddresses': []
            },
            Message={
                            'Subject': {'Data': sub},
                            'Body': {
                                'Html': {'Data': html}
                            }
                        },
            Source=self.from_address,
        )
            print("Sending the Cost Optimization report to "+ self.to_address)
        except ses.meta.client.exceptions.MessageRejected as ex:
            if ex.response['Error']['Message'] == 'MessageRejected':
                self.logger.warning('email not verified')
                print(ex.response['Error']['Message'])
            
        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in ses.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error("Error on line {} in ses.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
        
        