import logging
from botocore import exceptions
import sys
from utils.client import CLIENT
from aws.eip.pricing import Pricing


class EIP:
    '''To fetch information of all unused elastic IP's'''

    def __init__(self, config=None, regions=None):
        self.config = config['EBS']
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_eip(self, client):  # Returns information of existing elastic ip's in json format
        all_eip = client.describe_addresses()
        return all_eip['Addresses']

    def _get_savings(self, eip_list):   # Returns total possible savings
        savings = 0
        for eip in eip_list:
            savings = savings + eip[3]
        return round(savings, 2)

    def get_result(self):      # Returns a list of lists which contains headings and unused EIP information
        try:
            eip_list = []
            headers = ['Elastic_Ip', 'AWS_Region', 'Finding', 'Savings($)']

            for reg in self.regions:
                client_obj = CLIENT(reg)
                session, cloudwatch_client, pricing_client = client_obj.get_client()
                client = session.client('ec2')
                for address in self._describe_eip(client):
                    instance_id = private_ip = association_id = instance_state = ''
                    eip = []
                    finding = 'Unallocated'
                    if 'PrivateIpAddress' in address:
                        private_ip = address["PrivateIpAddress"]
                    if 'AssociationId' in address:
                        association_id = address['AssociationId']
                        if 'InstanceId' in address:
                            instance_id = address["InstanceId"]
                            response = client.describe_instances(InstanceIds=[instance_id])
                            for instance in response['Reservations'][0]['Instances']:
                                instance_state = instance['State']['Name']
                            if instance_state.lower() == 'stopped':
                                finding = 'Instance Stopped'
                            else:
                                finding = ''
                        else:
                            finding = ''
                    pricing = Pricing(pricing_client, reg)
                    if finding == 'Instance Stopped' or finding == 'Unallocated':
                        # An EIP is considered unused if it is attached with a stopped instance or is unallocated
                        price = pricing.get_eip_price()
                        eip.append(address["PublicIp"])
                        eip.append(reg)
                        eip.append(finding)
                        eip.append(round(price, 2))
                        eip_list.append(eip)
            # To fetch top 10 resources with maximum saving
            eip_sorted_list = sorted(eip_list, key=lambda x: x[3], reverse=True)
            total_savings = self._get_savings(eip_sorted_list[:10])
            return eip_sorted_list[:10], headers, total_savings

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in eip.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in eip.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
