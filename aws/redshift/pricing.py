import logging
from botocore import exceptions
import json
import sys
from utils.utils import get_region_name, get_price1

# Filters for get_products pricing api call used to fetch redshift price
node_filter = '[{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
              '{{"Field": "instanceType", "Value": "{it}", "Type": "TERM_MATCH"}},' \
              '{{"Field": "productFamily", "Value": "Compute Instance", "Type": "TERM_MATCH"}}]'

storage_filter = '[{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
                 '{{"Field": "productFamily", "Value": "Storage Snapshot", "Type": "TERM_MATCH"}}]'


class Pricing:
    '''For getting and returning the price of the RDS'''

    def __init__(self, pricing_client=None, region=None):
        self.pricing_client = pricing_client
        self.region = region
        self.formatted_region = get_region_name(region)
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def get_node_price(self, node_type):  # Returns redshift node price
        try:
            f = node_filter.format(r=self.formatted_region, it=node_type)
            data = self.pricing_client.get_products(ServiceCode='AmazonRedshift', Filters=json.loads(f))
            price = get_price1(data)
            return float(price)

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in redshift pricing.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error("Error on line {} in redshift pricing.py".format(sys.exc_info()[-1].tb_lineno) +
                              " | Message: " + str(e))
            sys.exit(1)

    def get_storage_price(self): # Returns redshift storage price
        try:
            f = storage_filter.format(r=self.formatted_region)
            data = self.pricing_client.get_products(ServiceCode='AmazonRedshift', Filters=json.loads(f))
            price = get_price1(data)
            return float(price)

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in redshift pricing.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error("Error on line {} in redshift pricing.py".format(sys.exc_info()[-1].tb_lineno) +
                              " | Message: " + str(e))
            sys.exit(1)
