import logging
from botocore import exceptions
import sys
from aws.elasticache.pricing import Pricing
from utils.client import Client
from utils.cloudwatch_utils import CloudwatchUtils
from utils.utils import handle_limit_exceeded_exception

class Elasticache:
    """To fetch information of all idle elasticache instances."""

    def __init__(self, headers, headers_inventory, config=None, regions=None):
        try:
         self.config = config.get('ELASTICACHE')
        except KeyError as e:
            self.logger.error(
                "Config for ELASTICACHE missing from config.cfg | Message: " + str(e))        
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_elasticache(self, client):  
        """Returns information of all existing Elasticache's in json format."""
        clusters = client.describe_cache_clusters()
        return clusters['CacheClusters']

    def _get_savings(self, ec_list):  
        """Returns total possible savings."""
        savings = 0
        for ec in ec_list:
            savings = savings + ec[10]
        return round(savings, 2)

    def _get_finding(self, cache_hit_miss_sum): 
        """Returns finding after checking if Elasticache is idle or not."""
        finding = ''
        #Idle elasticache check.
        if cache_hit_miss_sum == self.config['sumCacheHitMiss']:  
            finding = 'Idle'
        return finding

    def _get_clients(self, reg):
        """Fetches and returns clients."""
        client_obj = Client(reg)
        session, cloudwatch_client, pricing_client = client_obj.get_client()
        client = session.client('elasticache')
        cloudwatch = CloudwatchUtils(cloudwatch_client)
        pricing = Pricing(pricing_client, reg)
        return client, cloudwatch, pricing
        
    def _get_parameters(self, cache, reg, cloudwatch, pricing, ec_list, ec_inv_list):
        """Returns a list containing idle Elasticache instance information."""

        cache_id = cache["CacheClusterId"]
        cache_node_type = cache["CacheNodeType"]
        cache_engine = cache['Engine']
        if 'ReplicationGroupId' in cache:
            ReplicationGroupId = cache['ReplicationGroupId']
            cluster_name = ReplicationGroupId
        else:
            cluster_name = cache["CacheClusterId"]

        if cache['Engine'] == 'memcached':
            cache_hits = 'GetHits'
            cache_misses = 'GetMisses'
        else:
            cache_hits = 'CacheHits'
            cache_misses = 'CacheMisses'

        sum_hit = cloudwatch.get_sum_metric('AWS/ElastiCache', cache_hits,
                                            'CacheClusterId', cache["CacheClusterId"], self.config)
        sum_miss = cloudwatch.get_sum_metric('AWS/ElastiCache', cache_misses,
                                                'CacheClusterId', cache["CacheClusterId"], self.config)

        current_price = pricing.get_ec_price(cache_node_type)
        sum_cache_hit_miss = sum_hit + sum_miss
        finding = self._get_finding(sum_cache_hit_miss)
        savings = round(current_price, 2)
        if finding == 'Idle':
            #An Elasticache is considered idle if its cache hit and miss sum is 0.
            ec = [
                cache_id,
                cluster_name,
                "ELASTICACHE",
                cache_node_type,
                "-",
                cache_engine,
                reg,
                finding,
                self.config['cloudwatch_metrics_period'],
                f"{cache_hits}+{cache_misses} == {self.config['sumCacheHitMiss']}",
                savings
            ]
            ec_list.append(ec)
        else:
             ec_inv = [
                cache_id,
                cluster_name,
                "ELASTICACHE",
                cache_node_type,
                "-",
                cache_engine,
                reg
             ]
             ec_inv_list.append(ec_inv)
        return ec_list, ec_inv_list

    def get_result(self): 
        """Returns a list of lists which contains headings and idle Elasticache instance information."""
        try:
            ec_list = []
            ec_inv_list = []
            
            for reg in self.regions:
                client, cloudwatch, pricing = self._get_clients(reg)
                elasticache_clusters = self._describe_elasticache(client)
                for cache in elasticache_clusters:
                    ec_list = self._get_parameters(cache, reg, cloudwatch, pricing, ec_list)
                    
            #To fetch top 10 resources with maximum saving.
            ec_sorted_list = sorted(ec_list, key=lambda x: x[10], reverse=True)
            total_savings = self._get_savings(ec_sorted_list)
            return {'resource_list': ec_sorted_list, 'headers': self.headers, 'savings': total_savings}, {'headers_inv': self.headers_inventory, 'inv_list': ec_inv_list}

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'elasticache.py')
            sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in elasticache.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
