import logging
from botocore import exceptions
import sys
from aws.redshift.pricing import Pricing
from utils.client import CLIENT
from utils.cloudwatch_utils import CLOUDWATCH_UTILS


class REDSHIFT:
    '''To fetch information of all idle Redshift instances'''
    def __init__(self, config=None, regions=None):
        self.config = config['REDSHIFT']
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_redshift_clusters(self, client):  # Returns redshift cluster information in json format
        clusters = client.describe_clusters()
        return clusters['Clusters']

    def _get_savings(self, rs_list):   # Returns total savings
        savings = 0
        for rs in rs_list:
            savings = savings + rs[7]
        return round(savings, 2)

    def _get_rs_finding(self, db_connection_count):   # Returns finding if redshift instance is idle or not
        finding = ''
        if db_connection_count == 0:
            finding = 'Idle'
        return finding

    def get_result(self):   # Returns a list of lists which contains headings and idle redshift information
        try:
            rs_list = []
            headers = ['ClusterID', 'DBName', 'NodeType', 'NumberOfNodes', 'CreationDate', 'AWSRegion', 'Finding',
                       'Savings($)']
            for reg in self.regions:
                client_obj = CLIENT(reg)
                session, cloudwatch_client, pricing_client = client_obj.get_client()
                client = session.client('redshift')
                cloudwatch = CLOUDWATCH_UTILS(cloudwatch_client)
                for cluster in self._describe_redshift_clusters(client):
                    rs = []
                    pricing = Pricing(pricing_client, reg)
                    node_price = pricing.get_node_price(cluster['NodeType'])
                    db_connection_count = cloudwatch.get_sum_metric('AWS/Redshift', 'DatabaseConnections',
                                                                    'ClusterIdentifier', cluster['ClusterIdentifier'],
                                                                    self.config)
                    finding = self._get_rs_finding(db_connection_count)
                    savings = node_price * cluster['NumberOfNodes']

                    if finding == 'Idle':
                        # An redshift instance is considered to be idle if the db connection count = 0
                        rs.append(cluster['ClusterIdentifier'])
                        rs.append(cluster['DBName'])
                        rs.append(cluster['NodeType'])
                        rs.append(cluster['NumberOfNodes'])
                        rs.append(cluster['ClusterCreateTime'].strftime("%Y-%m-%d"))
                        rs.append(reg)
                        rs.append(finding)
                        rs.append(savings)
                        rs_list.append(rs)
            # To fetch top 10 resources with maximum saving
            rs_sorted_list = sorted(rs_list, key=lambda x: x[7], reverse=True)
            total_savings = self._get_savings(rs_sorted_list)
            return rs_sorted_list, headers, total_savings

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in redshift.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in redshift.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
