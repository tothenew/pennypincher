import logging
from botocore import exceptions
import sys
from aws.redshift.pricing import Pricing
from utils.client import Client
from utils.cloudwatch_utils import CloudwatchUtils
from utils.utils import handle_limit_exceeded_exception


class Redshift:
    """To fetch information of all idle Redshift instances."""
    
    def __init__(self, headers, headers_inventory, config=None, regions=None):
        try:
         self.config = config.get('REDSHIFT')
        except KeyError as e:
            self.logger.error(
                "Config for REDSHIFT missing from config.cfg | Message: " + str(e))       
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_redshift_clusters(self, client): 
        """Returns redshift cluster information in json format."""
        clusters = client.describe_clusters()
        return clusters['Clusters']

    def _get_savings(self, rs_list):   
        """Returns total savings."""
        savings = 0
        for rs in rs_list:
            savings = savings + rs[10]
        return round(savings, 2)

    def _get_rs_finding(self, db_connection_count):   
        """Returns finding if redshift instance is idle or not."""
        finding = ''
        if db_connection_count == self.config['dbConnectionCount']:
            finding = 'Idle'
        return finding

    def _get_clients(self, reg):
        """Fetches and returns clients."""
        client_obj = Client(reg)
        session, cloudwatch_client, pricing_client = client_obj.get_client()
        client = session.client('redshift')
        cloudwatch = CloudwatchUtils(cloudwatch_client)
        pricing = Pricing(pricing_client, reg)
        return client, cloudwatch, pricing

    def _get_parameters(self,cluster, reg, cloudwatch, pricing, rs_list, rs_inv_list ):
        """Returns a list containing idle redshift information."""        
        node_price = pricing.get_node_price(cluster['NodeType'])
        db_connection_count = cloudwatch.get_sum_metric('AWS/Redshift', 'DatabaseConnections',
                                                        'ClusterIdentifier', cluster['ClusterIdentifier'],
                                                        self.config)
        finding = self._get_rs_finding(db_connection_count)
        savings = node_price * cluster['NumberOfNodes']
        rs = []
        if finding == 'Idle':
            """ An redshift instance is considered to be idle if the db connection count = 0 """
            rs = [
            cluster['ClusterIdentifier'],
            cluster['DBName'],
            "REDSHIFT",
            cluster['NodeType'],
            cluster['VpcId'],
            "-",
            reg,
            finding,
            self.config['cloudwatch_metrics_period'],
            f"DatabaseConnections == {self.config['dbConnectionCount']}",
            savings
            ]
            rs_list.append(rs)
        else:
            rs_inv = [
            cluster['ClusterIdentifier'],
            cluster['DBName'],
            "REDSHIFT",
            cluster['NodeType'],
            cluster['VpcId'],
            "-",
            reg
             ]
            rs_inv_list.append(rs_inv)
        return rs_list, rs_inv_list

    def get_result(self):   
        """Returns a list of lists which contains headings and idle redshift information."""
        try:
            rs_list = []
            rs_inv_list = []
            
            for reg in self.regions:
                client, cloudwatch, pricing = self._get_clients(reg)
                for cluster in self._describe_redshift_clusters(client):
                    rs_list, rs_inv_list = self._get_parameters(cluster, reg, cloudwatch, pricing, rs_list, rs_inv_list)                    
                    
                    
            #To fetch top 10 resources with maximum saving.
            rs_sorted_list = sorted(rs_list, key=lambda x: x[10], reverse=True)
            total_savings = self._get_savings(rs_sorted_list)
            return {'resource_list': rs_sorted_list, 'headers': self.headers, 'savings': total_savings}, {'headers_inv': self.headers_inv, 'inv_list': rs_inv_list}

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'redshift.py')
            sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in redshift.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
