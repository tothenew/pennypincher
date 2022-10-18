import logging
from botocore import exceptions
import sys
from utils.client import Client
from aws.eip.pricing import Pricing
from utils.utils import handle_limit_exceeded_exception


class ElasticIP:
    """To fetch information of all unused elastic IP's."""

    def __init__(self, regions=None):   
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_eip(self, client):
        """Returns information of existing elastic ip's in json format."""
        all_eip = client.describe_addresses()
        return all_eip['Addresses']

    def _get_savings(self, eip_list):   
        """Returns total possible savings."""
        savings = 0
        for eip in eip_list:
            savings = savings + eip[10]
        return round(savings, 2)
    
    def _get_clients(self, reg):
        """Fetches and returns clients."""
        client_obj = Client(reg)
        session, cloudwatch_client, pricing_client = client_obj.get_client()
        client = session.client('ec2')
        pricing = Pricing(pricing_client, reg)
        return client, pricing

    def _get_parameters(self, address, reg, client, pricing, eip_list):
        """Returns a list containing unused EIP information."""
        
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
        if finding == 'Instance Stopped' or finding == 'Unallocated':
            #An EIP is considered unused if it is attached with a stopped instance or is unallocated.
            price = pricing.get_eip_price()
            eip = [
            address["PublicIp"],
            address["PublicIp"],
            "EIP",
            "-",
            "-",
            "-",
            reg,
            finding,
            14,
            "Metric",
            round(price, 2)
            ]
            eip_list.append(eip)
        return eip_list

    def get_result(self):     
        """Returns a list of lists which contains headings and unused EIP information."""
        try:
            eip_list = []
            headers=[   'ResourceID','ResouceName','ServiceName','Type','VPC',
                        'State','Region','Finding','EvaluationPeriod','Metric','Saving($)'
                    ]

            for reg in self.regions:
                client, pricing = self._get_clients(reg)
                for address in self._describe_eip(client):
                        eip_list = self._get_parameters(address, reg, client, pricing, eip_list)
                        
            #To fetch top 10 resources with maximum saving.
            eip_sorted_list = sorted(eip_list, key=lambda x: x[10], reverse=True)
            total_savings = self._get_savings(eip_sorted_list[:11])
            return {'resource_list': eip_sorted_list[:10], 'headers': headers, 'savings': total_savings}

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'eip.py')
            sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in eip.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)
