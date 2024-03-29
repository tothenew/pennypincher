import logging
from botocore import exceptions
import json
import sys
from utils.utils import get_region_name, get_price1, get_price2, handle_limit_exceeded_exception


class Pricing:
    """For getting and returning the price of the Elastic IP's."""

    #Filter for get_products pricing api call used to fetch EIP price.
    eip_filter = '[{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
                 ' {{"Field": "group", "Value": "ElasticIP:Address", "Type": "TERM_MATCH"}},' \
                 '{{"Field": "productFamily", "Value": "IP Address", "Type": "TERM_MATCH"}}]'
    
    def __init__(self, pricing_client=None, region=None):
        self.pricing_client = pricing_client
        self.region = region
        self.formatted_region = get_region_name(region)
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()
    
    def get_eip_price(self):          
        """Returns EIP price."""
        try:
            f = self.eip_filter.format(r=self.formatted_region)
            data = self.pricing_client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
            if "eu-west-1" in self.region:
                price = get_price2(data)
                return float(price)
            price = get_price1(data)
            return float(price)
        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'eip pricing.py')
            sys.exit(1)

        except Exception as e:
            print("Error on line {} in eip pricing.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            # sys.exit(1)
