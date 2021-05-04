import logging
from botocore import exceptions
import json
import sys
from utils.utils import get_region_name, get_price

# Filters for get_products pricing api call used to fetch EBS price
ebs_storage_filter = '[{{"Field": "volumeType", "Value": "{vn}", "Type": "TERM_MATCH"}},' \
                     '{{"Field": "productFamily", "Value": "Storage", "Type": "TERM_MATCH"}},' \
                     '{{"Field": "volumeApiName", "Value": "{v}", "Type": "TERM_MATCH"}},' \
                     '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}}]'

ebs_iops_filter = '[{{"Field": "group", "Value": "EBS IOPS", "Type": "TERM_MATCH"}},' \
                  '{{"Field": "productFamily", "Value": "System Operation", "Type": "TERM_MATCH"}},' \
                  '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}}]'


class Pricing:
    '''For getting and returning the price of the EBS volumes'''

    def __init__(self, pricing_client=None, region=None):
        self.pricing_client = pricing_client
        self.region = region
        self.formatted_region = get_region_name(region)
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _get_volume_name(self, volume_type):
        ebs_storage_mapping = {'gp2': 'General Purpose', 'io1': 'Provisioned IOPS', 'sc1': 'Cold HDD',
                               'io2': 'Provisioned IOPS', 'st1': 'Throughput Optimized HDD', 'standard': 'Magnetic'}
        return ebs_storage_mapping.get(volume_type)

    def get_ebs_iops_price(self, volume_type):  # Returns price of ebs with iops configured
        iops_price = 0

        try:
            if volume_type == 'io1' or volume_type == 'io2':
                f = ebs_iops_filter.format(r=self.formatted_region)
                data = self.pricing_client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
                iops_price = get_price(data)
                return iops_price
            else:
                return iops_price

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in ebs pricing.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            print("Error on line {} in ebs pricing.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)

    def get_ebs_storage_price(self, volume_type):  # Returns price of EBS based on its size
        try:
            volume_name = self._get_volume_name(volume_type)
            f = ebs_storage_filter.format(v=volume_type, r=self.formatted_region, vn=volume_name)
            data = self.pricing_client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
            storage_price = get_price(data)
            return float(storage_price)

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in ebs pricing.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in ebs pricing.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)
