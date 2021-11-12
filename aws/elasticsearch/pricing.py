import logging
from botocore import exceptions
import sys
import json
from utils.utils import get_region_name, get_price1, get_price, handle_limit_exceeded_exception

class Pricing:
    """For getting and returning the price of the Elasticsearch instance."""

    #Filter for get_products pricing api call used to fetch elasticsearch price.
    elasticsearch_filter = '[{{"Field": "instanceType", "Value": "{i}", "Type": "TERM_MATCH"}},' \
                           '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}}]'

    elasticsearch_storage_filter = '[{{"Field": "storageMedia", "Value": "{s}", "Type": "TERM_MATCH"}},' \
                                   '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}}]'


    def __init__(self, pricing_client=None, region=None):
        self.pricing_client = pricing_client
        self.region = region
        self.formatted_region = get_region_name(region)
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    #PIOPS gets the IOPS price, PIOPS-Storage gets the io1 storage price.
    def _get_es_storage(self, storage):
        es_storage_mapping = {'Managed': 'Managed-Storage', 'standard': 'Magnetic', 'io1': 'PIOPS-Storage',
                              'gp2': 'GP2', 'iops': 'PIOPS'}
        return es_storage_mapping.get(storage)

    def get_es_price(self, instance_type, storage_type, volume_size, iops_count):  
        """Returns elasticsearch price."""
        iops_price = 0
        try:
            storage_type = self._get_es_storage(storage_type)
            instance_type = instance_type.replace("elasticsearch", "search")
            f = self.elasticsearch_filter.format(r=self.formatted_region, i=instance_type, )
            instance_data = self.pricing_client.get_products(ServiceCode='AmazonES', Filters=json.loads(f))
            instance_price = get_price1(instance_data)
            f = self.elasticsearch_storage_filter.format(r=self.formatted_region, s=storage_type)
            storage_data = self.pricing_client.get_products(ServiceCode='AmazonES', Filters=json.loads(f))
            storage_price = get_price(storage_data) * volume_size
            if iops_count:
                storage_type = self._get_es_storage('iops')
                f = self.elasticsearch_storage_filter.format(r=self.formatted_region, s=storage_type)
                iops_data = self.pricing_client.get_products(ServiceCode='AmazonES', Filters=json.loads(f))
                iops_price = get_price(iops_data) * iops_count
            total_price = instance_price + storage_price + iops_price
            return float(total_price)

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'elasticsearch pricing.py')
            sys.exit(1)

        except Exception as e:
            self.logger.error("Error on line {} in elasticsearch pricing.py".format(sys.exc_info()[-1].tb_lineno) +
                              " | Message: " + str(e))
            sys.exit(1)
