import logging
from botocore import exceptions
import sys
from aws.elasticsearch.pricing import Pricing
from utils.client import Client
from utils.cloudwatch_utils import CloudwatchUtils
from utils.utils import handle_limit_exceeded_exception


class Elasticsearch:
    """To fetch information of all idle elasticsearch instances."""

    def __init__(self, config=None, regions=None):
        try:
         self.config = config.get('ELASTICSEARCH')
        except KeyError as e:
            self.logger.error(
                "Config for ELASTICSEARCH missing from config.cfg | Message: " + str(e))       
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _list_elasticsearch(self, client):  
        """Returns list of elasticsearch domains."""
        domain_list = client.list_domain_names()
        return domain_list['DomainNames']

    def _describe_elasticsearch(self, client, domain_name):  
        """Returns information regarding an elasticsearch in json."""
        es_data = client.describe_elasticsearch_domain(DomainName=domain_name)
        return es_data['DomainStatus']

    def _get_es_finding(self, idle_instance_check):  
        """Returns finding if an elasticsearch instance is Idle or not."""
        finding = ''
        if idle_instance_check == 0:  
            #Idle instance check.
            finding = 'Idle'
        return finding

    def _get_savings(self, es_list):  
        """Returns total possible savings."""
        savings = 0
        for es in es_list:
            savings = savings + es[10]
        return round(savings, 2)

    def _get_clients(self, reg):
        """Fetches and returns clients."""
        client_obj = Client(reg)
        session, cloudwatch_client, pricing_client = client_obj.get_client()
        client = session.client('es')
        cloudwatch = CloudwatchUtils(cloudwatch_client)
        pricing = Pricing(pricing_client, reg)
        return client, cloudwatch, pricing

    def _get_parameters(self, es, reg, cloudwatch, pricing, es_list):    
        """Returns list containing idle Elasticsearch instance information."""               
        elasticsearch = []
        monthly_cost_master = 0                 
        iops = volume_size = 0
        if es['EBSOptions']['EBSEnabled']:
            storage_type = es['EBSOptions']['VolumeType']
            volume_size = es['EBSOptions']['VolumeSize']
            if 'Iops' in es['EBSOptions']:
                iops = es['EBSOptions']['Iops']
        else:
            storage_type = 'Managed'

        client_id = es['ARN'].split(':')[4]
        instance_type = es["ElasticsearchClusterConfig"]["InstanceType"]
        instance_count = es["ElasticsearchClusterConfig"]["InstanceCount"]
        monthly_cost_data = pricing.get_es_price(instance_type, storage_type, volume_size,
                                                    iops) * instance_count

        dedicated_master_type = 'N/A'
        dedicated_master_count = 'N/A'

        if es["ElasticsearchClusterConfig"]["DedicatedMasterEnabled"] == True:
            dedicated_master_type = es["ElasticsearchClusterConfig"]["DedicatedMasterType"]
            dedicated_master_count = es["ElasticsearchClusterConfig"]["DedicatedMasterCount"]
            monthly_cost_master = pricing.get_es_price(dedicated_master_type, storage_type, volume_size,
                                                        iops) * dedicated_master_count

        sum_instance_indexing_rate = cloudwatch.get_sum_metric2('AWS/ES', 'IndexingRate', 'ClientId',
                                                                client_id,
                                                                'DomainName', es["DomainName"], self.config)

        sum_instance_search_rate = cloudwatch.get_sum_metric2('AWS/ES', 'SearchRate', 'ClientId', client_id,
                                                                'DomainName', es["DomainName"], self.config)
        idle_instance_count = sum_instance_search_rate + sum_instance_indexing_rate
        finding = self._get_es_finding(idle_instance_count)
        if finding == 'Idle':
            #An elasticsearch instance is considered idle if sum of indexing rate and search rate = 0.
            elasticsearch = [
                es["DomainName"],
                es["DomainName"],
                "ELASTICSEARCH",
                instance_type,
                es['VPCOptions']['VPCId'],
                instance_count,
                reg,
                finding,
                14,
                "Metric",
                round(monthly_cost_master + monthly_cost_data, 2)
            ]
            es_list.append(elasticsearch)
        return es_list
    
    def get_result(self):  
        """Returns a list of lists which contains headings and idle Elasticsearch instance information."""
        try:
            es_list = []
            headers=[   'ResourceID','ResouceName','ServiceName','Type','VPC',
                        'State','Region','Finding','EvaluationPeriod','Metric','Saving($)'
                    ]
  
            for reg in self.regions:
                client, cloudwatch, pricing = self._get_clients(reg)
                for domainName in self._list_elasticsearch(client):
                    es = self._describe_elasticsearch(client, domainName["DomainName"])
                    es_list= self._get_parameters(es, reg, cloudwatch, pricing, es_list)
                    

            #To fetch top 10 resources with maximum saving.
            es_sorted_list = sorted(es_list, key=lambda x: x[10], reverse=True)
            total_savings = self._get_savings(es_sorted_list)
            return {'resource_list': es_sorted_list, 'headers': headers, 'savings': total_savings}

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'elasticsearch.py')
            sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in elasticsearch.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)
