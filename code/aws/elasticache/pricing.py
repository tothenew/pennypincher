import logging
from botocore import exceptions
import sys
import json
from utils.utils import get_region_name, get_price1, handle_limit_exceeded_exception

class Pricing:
    """For getting and returning the price of the Elasticache instance."""
    
    #Filter for get_products pricing api call used to fetch elasticache price.
    elasticache_filter = '[{{"Field": "instanceType", "Value": "{i}", "Type": "TERM_MATCH"}},' \
                         '{{"Field": "locationType", "Value": "AWS Region", "Type": "TERM_MATCH"}},' \
                         '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}}]'
    

    def __init__(self, pricing_client=None, region=None):
        self.pricing_client = pricing_client
        self.region = region
        self.formatted_region = get_region_name(region)
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()
  

    def get_ec_price(self, instance_type):
        """Returns elasticache price."""
        try:
            f = self.elasticache_filter.format(i=instance_type, r=self.formatted_region)
            data = self.pricing_client.get_products(ServiceCode='AmazonElastiCache', Filters=json.loads(f))
            price = get_price1(data)
            return float(price)

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'elasticache pricing.py')
            sys.exit(1)

        except Exception as e:
            self.logger.error("Error on line {} in elasticache pricing.py".format(sys.exc_info()[-1].tb_lineno) +
                              " | Message: " + str(e))
            sys.exit(1)
