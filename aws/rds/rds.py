import logging
from botocore import exceptions
import sys
import datetime
from aws.rds.pricing import Pricing
from utils.client import Client
from utils.cloudwatch_utils import CloudwatchUtils
from utils.utils import handle_limit_exceeded_exception

class RelationalDatabaseService:
    """To fetch information of all idle RDS instances."""
    
    def __init__(self, config=None, regions=None):
        try:
         self.config = config.get('RDS')
        except KeyError as e:
            self.logger.error(
                "Config for RDS missing from config.cfg | Message: " + str(e))       
        self.regions = regions
        self.numberOfDays = int(self.config['cloudwatch_metrics_days'])
        self.now = datetime.datetime.utcnow()
        self.start = (self.now - datetime.timedelta(days=self.numberOfDays)).strftime('%Y-%m-%d')
        self.end = self.now.strftime('%Y-%m-%d')
        self.period = int(self.config['cloudwatch_metrics_period'])
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_rds(self, client):    
        """Returns RDS instance information in json format."""
        response = client.describe_db_instances()
        return response['DBInstances']

    def _get_rds_finding(self, connection_count):  
        """Returns finding if RDS instance is idle or not."""
        finding = ''
        if connection_count == 0:
            finding = 'Idle'
        return finding

    def _get_savings(self, rds_list): 
        """Returns total possible savings."""
        savings = 0
        for rds in rds_list:
            savings = savings + rds[10]
        return round(savings, 2)

    def _get_clients(self, reg):
        """Fetches and returns clients."""
        client_obj = Client(reg)
        session, cloudwatch_client, pricing_client = client_obj.get_client()
        client = session.client('rds')
        cloudwatch = CloudwatchUtils(cloudwatch_client)
        pricing = Pricing(pricing_client, reg)
        return client, cloudwatch, pricing
   
    def _get_parameters(self, rds_instance, reg, cloudwatch, pricing, rds_list):
        """Returns a list containing idle RDS information."""    
        rds = []
        iops = 0
        if 'iops' in rds_instance.keys():
            iops = rds_instance['Iops']

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
            #An RDS instance is classified as idle if the connection count = 0.
            savings = round(db_cost + storage_cost, 2)
            rds =[
                rds_instance["DBInstanceIdentifier"],
                rds_instance["DBInstanceIdentifier"],
                "RDS",
                rds_instance["DBInstanceClass"],
                rds_instance['DBSubnetGroup']['VpcId'],
                rds_instance["DBInstanceStatus"],
                reg,
                finding,
                self.config['cloudwatch_metrics_period'],
                "DatabaseConnections == 0",
                savings
               ]
            rds_list.append(rds)
        return rds_list


    def get_result(self):     
        """Returns a list of lists which contains headings and idle RDS information."""
        try:
            rds_list = []
            headers=[   'ResourceID','ResouceName','ServiceName','Type','VPC',
                        'State','Region','Finding','EvaluationPeriod (seconds)','Metric','Saving($)'
                    ]

            for reg in self.regions:
                client, cloudwatch, pricing = self._get_clients(reg)
                for rds_instance in self._describe_rds(client):
                        rds_list = self._get_parameters(rds_instance, reg, cloudwatch, pricing, rds_list)
                        
            #To fetch top 10 resources with maximum saving.
            rds_sorted_list = sorted(rds_list, key=lambda x: x[10], reverse=True)
            total_savings = self._get_savings(rds_sorted_list)
            return {'resource_list': rds_sorted_list, 'headers': headers, 'savings': total_savings}

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'rds.py')
            sys.exit(1)

        except Exception as e:
            self.logger.error("Error on line {} in rds.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
