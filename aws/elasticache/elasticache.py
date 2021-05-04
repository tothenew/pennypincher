import logging
from botocore import exceptions
import sys
from aws.elasticache.pricing import Pricing
from utils.cloudwatch_utils import CLOUDWATCH_UTILS
from utils.client import CLIENT


class ELASTICACHE:
    '''To fetch information of all idle elasticache instances'''

    def __init__(self, config=None, regions=None):
        self.config = config['ELASTICACHE']
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_elasticache(self, client):  # Returns information of all existing Elasticache's in json format
        clusters = client.describe_cache_clusters()
        return clusters['CacheClusters']

    def _get_savings(self, ec_list):  # Returns total possible savings
        savings = 0
        for ec in ec_list:
            savings = savings + ec[7]
        return round(savings, 2)

    def _get_finding(self, cache_hit_miss_sum):  # Returns finding after checking if Elasticache is idle or not
        finding = ''
        if cache_hit_miss_sum == 0:  # Idle elasticache check
            finding = 'Idle'
        return finding

    def get_result(self):  # Returns a list of lists which contains headings and idle Elasticache instance information
        try:
            ec_list = []
            headers = ['NodeId', 'ClusterName', 'CacheNodeType', 'Engine', 'CreationDate', 'AWSRegion',
                       'Finding', 'Savings($)']
            for reg in self.regions:
                client_obj = CLIENT(reg)
                session, cloudwatch_client, pricing_client = client_obj.get_client()
                client = session.client('elasticache')
                elasticache_clusters = self._describe_elasticache(client)
                for cache in elasticache_clusters:
                    ec = []
                    cache_id = cache["CacheClusterId"]
                    cache_node_type = cache["CacheNodeType"]
                    cache_engine = cache['Engine']
                    if 'ReplicationGroupId' in cache:
                        ReplicationGroupId = cache['ReplicationGroupId']
                        cluster_name = ReplicationGroupId
                    else:
                        cluster_name = cache["CacheClusterId"]
                    cloudwatch = CLOUDWATCH_UTILS(cloudwatch_client)

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

                    pricing = Pricing(pricing_client, reg)
                    current_price = pricing.get_ec_price(cache_node_type)
                    sum_cache_hit_miss = sum_hit + sum_miss
                    finding = self._get_finding(sum_cache_hit_miss)
                    savings = round(current_price, 2)
                    if finding == 'Idle':
                        # An Elasticache is considered idle if its cache hit and miss sum is 0
                        ec.append(cache_id)
                        ec.append(cluster_name)
                        ec.append(cache_node_type)
                        ec.append(cache_engine)
                        ec.append(cache['CacheClusterCreateTime'].date())
                        ec.append(reg)
                        ec.append(finding)
                        ec.append(savings)
                        ec_list.append(ec)
            # To fetch top 10 resources with maximum saving
            ec_sorted_list = sorted(ec_list, key=lambda x: x[7], reverse=True)
            total_savings = self._get_savings(ec_sorted_list)
            return ec_sorted_list, headers, total_savings

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in elasticache.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in elasticache.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
