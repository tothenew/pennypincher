import logging
from botocore import exceptions
import sys
import datetime
from utils.cloudwatch_utils import CLOUDWATCH_UTILS
from aws.rds.pricing import Pricing
from utils.client import CLIENT


class RDS:
    '''To fetch information of all idle RDS instances'''
    def __init__(self, config=None, regions=None):
        self.config = config['RDS']
        self.regions = regions
        self.numberOfDays = int(self.config['cloudwatch_metrics_days'])
        self.now = datetime.datetime.utcnow()
        self.start = (self.now - datetime.timedelta(days=self.numberOfDays)).strftime('%Y-%m-%d')
        self.end = self.now.strftime('%Y-%m-%d')
        self.period = int(self.config['cloudwatch_metrics_period'])
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_rds(self, client):    # Returns RDS instance information in json format
        response = client.describe_db_instances()
        return response['DBInstances']

    def _get_rds_finding(self, connection_count):  # Returns finding if RDS instance is idle or not
        finding = ''
        if connection_count == 0:
            finding = 'Idle'
        return finding

    def _get_savings(self, rds_list): # Returns total possible savings
        savings = 0
        for rds in rds_list:
            savings = savings + rds[8]
        return round(savings, 2)

    def get_result(self):     # Returns a list of lists which contains headings and idle RDS information
        try:
            rds_list = []
            headers = ['InstanceIdentifier', 'InstanceClass', 'InstanceState',
                       'StorageType', 'ProvisionStorage', 'CreationDate', 'AWSRegion',
                       'Finding', 'Savings($)']

            for reg in self.regions:
                client_obj = CLIENT(reg)
                session, cloudwatch_client, pricing_client = client_obj.get_client()
                client = session.client('rds')
                cloudwatch = CLOUDWATCH_UTILS(cloudwatch_client)
                for rds_instance in self._describe_rds(client):
                    rds = []
                    iops = 0
                    if 'iops' in rds_instance.keys():
                        iops = rds_instance['Iops']

                    pricing = Pricing(pricing_client, reg)
                    db_cost, storage_cost = pricing.get_rds_price(rds_instance["Engine"],
                                                                  rds_instance['DBInstanceClass'],
                                                                  rds_instance['MultiAZ'], rds_instance['LicenseModel'],
                                                                  rds_instance['StorageType'],
                                                                  rds_instance['AllocatedStorage'],
                                                                  iops)

                    avg_cpu, avg_cpu = cloudwatch.get_avg_max_metric('AWS/RDS', 'CPUUtilization',
                                                                     'DBInstanceIdentifier',
                                                                     rds_instance["DBInstanceIdentifier"], self.config)
                    connection_count = cloudwatch.get_sum_metric('AWS/RDS', 'DatabaseConnections',
                                                                 'DBInstanceIdentifier'
                                                                 , rds_instance["DBInstanceIdentifier"], self.config)
                    free_storage = cloudwatch.get_avg_metric('AWS/RDS', 'FreeStorageSpace',
                                                             'DBInstanceIdentifier'
                                                             , rds_instance["DBInstanceIdentifier"], self.config)
                    free_memory = cloudwatch.get_avg_metric('AWS/RDS', 'FreeableMemory',
                                                            'DBInstanceIdentifier'
                                                            , rds_instance["DBInstanceIdentifier"], self.config)
                    finding = self._get_rds_finding(connection_count)

                    if finding == 'Idle':
                        # An RDS instance is classified as idle if the connection count = 0
                        rds.append(rds_instance["DBInstanceIdentifier"])
                        rds.append(rds_instance["DBInstanceClass"])
                        rds.append(rds_instance["DBInstanceStatus"])
                        rds.append(rds_instance['StorageType'])
                        rds.append(str(rds_instance['AllocatedStorage']) + ' GB')
                        rds.append(str(rds_instance['InstanceCreateTime'].date()))
                        rds.append(reg)
                        rds.append(finding)
                        savings = round(db_cost + storage_cost, 2)
                        rds.append(savings)
                        rds_list.append(rds)
            # To fetch top 10 resources with maximum saving
            rds_sorted_list = sorted(rds_list, key=lambda x: x[8], reverse=True)
            total_savings = self._get_savings(rds_sorted_list)
            return rds_sorted_list, headers, total_savings

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in rds.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error("Error on line {} in rds.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
