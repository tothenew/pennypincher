import logging
from botocore import exceptions
import sys
from datetime import datetime, timedelta, timezone
from utils.utils import get_backup_age
from aws.ebs.pricing import Pricing
from utils.client import CLIENT
from utils.cloudwatch_utils import CLOUDWATCH_UTILS


class EBS:
    '''To fetch information of all unused EBS volumes'''

    def __init__(self, config=None, regions=None):
        self.config = config['EBS']
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_ebs(self, client):  # Returns information of all existing ebs volumes in json format
        response = client.describe_volumes(Filters=[
            {
                'Name': 'status',
                'Values': [
                    'available', 'in-use'
                ]
            },
        ])
        return response['Volumes']

    def _get_savings(self, ebs_list):  # Returns total possible savings
        savings = 0
        for ebs in ebs_list:
            savings = savings + ebs[9]
        return round(savings, 2)

    def get_result(self):  # Returns a list of lists which contains headings and idle EBS information
        try:
            ebs_list = []
            headers = ["VolumeId", "State", "Type", "SizeGB", 'Iops', 'CreationDate', 'Age',
                       "AWSRegion", "Finding", "Savings($)"]
            for reg in self.regions:
                client_obj = CLIENT(reg)
                session, cloudwatch_client, pricing_client = client_obj.get_client()
                client = session.client('ec2')
                for vol in self._describe_ebs(client):
                    ebs = []
                    iops = 0
                    finding = ''
                    create_time = vol['CreateTime']
                    creation_date = datetime.strptime(str(create_time).split(' ')[0], '%Y-%m-%d').date()
                    age = get_backup_age(creation_date)
                    cloudwatch_period = datetime.now(timezone.utc) - timedelta(days=15)
                    if 'Iops' in vol:
                        iops = int(vol['Iops'])

                    if vol["State"] == 'available':
                        finding = 'Available'  # Check if EBS is in available state

                    elif vol["State"] == 'in-use' and create_time <= cloudwatch_period:
                        cloudwatch = CLOUDWATCH_UTILS(cloudwatch_client)
                        DiskReadOps = cloudwatch.get_sum_metric('AWS/EBS', 'VolumeReadOps',
                                                                'VolumeId', vol["VolumeId"], self.config)
                        DiskWriteOps = cloudwatch.get_sum_metric('AWS/EBS', 'VolumeWriteOps',
                                                                 'VolumeId', vol["VolumeId"], self.config)
                        if (DiskReadOps + DiskWriteOps) == 0:  # Check if EBS is unused
                            finding = 'Unused'

                    pricing = Pricing(pricing_client, reg)
                    storage_price = pricing.get_ebs_storage_price(vol["VolumeType"])
                    iops_price = pricing.get_ebs_iops_price(vol["VolumeType"])
                    savings = storage_price * float(vol["Size"]) + iops_price * iops
                    if finding == 'Unused' or finding == 'Available':
                        # An EBS is considered idle if it's finding comes out to be 'Unused' or 'Available'
                        ebs.append(vol["VolumeId"])
                        ebs.append(vol["State"])
                        ebs.append(vol["VolumeType"])
                        ebs.append(vol["Size"])
                        ebs.append(iops)
                        ebs.append(creation_date)
                        ebs.append(age)
                        ebs.append(reg)
                        ebs.append(finding)
                        ebs.append(round(savings, 2))
                        ebs_list.append(ebs)
            # To fetch top 10 resources with maximum saving
            ebs_sorted_list = sorted(ebs_list, key=lambda x: x[9], reverse=True)
            total_savings = self._get_savings(ebs_sorted_list[:10])
            return ebs_sorted_list[:10], headers, total_savings

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in ebs.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)
        except Exception as e:
            self.logger.error(
                "Error on line {} in ebs.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
