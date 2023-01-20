import logging
from botocore import exceptions
import sys
import json
from utils.utils import get_region_name, get_region_code, get_price1, handle_limit_exceeded_exception

class Pricing:
    """For getting and returning the price of the Loadbalancers."""
    
    #Filters for get_products pricing api call used to fetch loadbalancer price.
    lb_filter = '[{{"Field": "productFamily", "Value": "{pf}", "Type": "TERM_MATCH"}},' \
                '{{"Field": "usageType", "Value": "{ut}", "Type": "TERM_MATCH"}},' \
                '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}}]'

    def __init__(self, pricing_client=None, region=None):
        self.pricing_client = pricing_client
        self.region = region
        self.formatted_region = get_region_name(region)
        self.region_code = get_region_code(region)
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()


    def get_lb_price(self, product_family):    
        """Returns loadbalancer price."""
        price = 0
        try:
            if self.region == 'us-east-1':
                usageType = 'LoadBalancerUsage'
            else:
                usageType = str(self.region_code) + '-LoadBalancerUsage'
            f = self.lb_filter.format(r=self.formatted_region, pf=product_family, ut=usageType)
            data = self.pricing_client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
            price = get_price1(data)
            return float(price)

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'loadbalancer pricing.py')
            sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in loadbalancer pricing.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            # sys.exit(1)
