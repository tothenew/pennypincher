import logging
from botocore import exceptions
import sys
from datetime import datetime, timedelta, timezone
from utils.utils import get_backup_age, handle_limit_exceeded_exception
from aws.ebs.pricing import Pricing
from utils.client import Client
from utils.cloudwatch_utils import CloudwatchUtils


class ElasticBlockStore:
    """To fetch information of all unused EBS volumes."""

    def __init__(self, config=None, regions=None):
        try:
         self.config = config.get('EBS')
        except KeyError as e:
            self.logger.error(
                "Config for EBS missing from config.cfg | Message: " + str(e))  
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_ebs(self, client): 
        """Returns information of all existing ebs volumes in json format."""
        response = client.describe_volumes(Filters=[
            {
                'Name': 'status',
                'Values': [
                    'available', 'in-use'
                ]
            },
        ])
        return response['Volumes']

    def _get_savings(self, ebs_list):  
        """Returns total possible savings."""
        savings = 0
        for ebs in ebs_list:
            savings = savings + ebs[10]
        return round(savings, 2)

    def _get_clients(self, reg):
        """Fetches and returns clients."""
        client_obj = Client(reg)
        session, cloudwatch_client, pricing_client = client_obj.get_client()
        client = session.client('ec2')
        cloudwatch = CloudwatchUtils(cloudwatch_client)
        pricing = Pricing(pricing_client, reg)
        return client, cloudwatch, pricing
    
    def _get_parameters(self, vol, reg, cloudwatch, pricing, ebs_list):
        """Returns a list containing idle EBS information."""
        ebs = []
        iops = 0
        finding = ''
        create_time = vol['CreateTime']
        creation_date = datetime.strptime(str(create_time).split(' ')[0], '%Y-%m-%d').date()
        age = get_backup_age(creation_date)
        cloudwatch_period = datetime.now(timezone.utc) - timedelta(days=15)
        if 'Iops' in vol:
            iops = int(vol['Iops'])

        #Check if EBS is in available state
        if vol["State"] == 'available':
            finding = 'Available'  

        elif vol["State"] == 'in-use' and create_time <= cloudwatch_period:
            
            DiskReadOps = cloudwatch.get_sum_metric('AWS/EBS', 'VolumeReadOps',
                                                    'VolumeId', vol["VolumeId"], self.config)
            DiskWriteOps = cloudwatch.get_sum_metric('AWS/EBS', 'VolumeWriteOps',
                                                        'VolumeId', vol["VolumeId"], self.config)
            #Check if EBS is unused
            if (DiskReadOps + DiskWriteOps) == 0:  
                finding = 'Unused'

        
        storage_price = pricing.get_ebs_storage_price(vol["VolumeType"])
        iops_price = pricing.get_ebs_iops_price(vol["VolumeType"])
        savings = storage_price * float(vol["Size"]) + iops_price * iops
        if finding == 'Unused' or finding == 'Available':
            #An EBS is considered idle if it's finding comes out to be 'Unused' or 'Available'.
            ebs = [
                vol["VolumeId"],
                vol["VolumeId"],
                "EBS",
                vol["VolumeType"],
                "-",
                vol["State"],
                vol["AvailabilityZone"],
                finding,
                14,
                "Metric",
                round(savings, 2)
               ]
            ebs_list.append(ebs)
        return ebs_list


    def get_result(self):  
        """Returns a list of lists which contains headings and idle EBS information."""
        try:
            ebs_list = []
            headers=[   'ResourceID','ResouceName','ServiceName','Type','VPC',
                        'State','Region','Finding','EvaluationPeriod','Metric','Saving($)'
                    ]
            for reg in self.regions:
                client, cloudwatch, pricing = self._get_clients(reg)
                for vol in self._describe_ebs(client):
                    ebs_list = self._get_parameters(vol, reg, cloudwatch, pricing, ebs_list)
            
            #To fetch top 10 resources with maximum saving.
            ebs_sorted_list = sorted(ebs_list, key=lambda x: x[10], reverse=True)
            total_savings = self._get_savings(ebs_sorted_list[:11])
            return { 'resource_list': ebs_sorted_list[:11], 'headers': headers, 'savings': total_savings }

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'ebs.py')
            sys.exit(1)
        except Exception as e:
            self.logger.error(
                "Error on line {} in ebs.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)


 

