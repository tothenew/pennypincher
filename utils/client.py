import boto3
import logging
from botocore import exceptions
import sys


class CLIENT:
    '''Returns boto3 session, cloudwatch client and pricing client'''
    def __init__(self, region=None):
        self.region = region
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _get_session(self):    # Returns boto3 session
        self.session = boto3.Session(region_name=self.region)
        return self.session

    def _get_cloudwatch_client(self):   # Returns cloudwatch client
        cloudwatch_client = self.session.client('cloudwatch')
        return cloudwatch_client

    def _get_pricing_client(self):   # Returns pricing client
        pricing_client = self.session.client('pricing', region_name='us-east-1')
        return pricing_client

    def get_client(self):  # Returns session, cloudwatch client and pricing client all together
        try:
            session = self._get_session()
            cloudwatch_client = self._get_cloudwatch_client()
            pricing_client = self._get_pricing_client()
            return session, cloudwatch_client, pricing_client

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in client.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error("Error on line {} in client.py".format(sys.exc_info()[-1].tb_lineno) +
                              " | Message: " + str(e))
            sys.exit(1)
