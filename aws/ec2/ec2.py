import logging
from botocore import exceptions
import sys
from utils.client import Client
from utils.cloudwatch_utils import CloudwatchUtils
from aws.ec2.pricing import Pricing


class ElasticComputeCloud:
    """To fetch information of all idle EC2's."""

    def __init__(self, config=None, regions=None):
        self.config = config['EC2']
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _get_image_info(self, client, image_id): 
        """Returns AMI information."""
        response = client.describe_images(ImageIds=[image_id])
        return response['Images']

    def _get_savings(self, ec2_list):  
        """Returns total possible savings."""
        savings = 0
        for ec2 in ec2_list:
            savings = savings + ec2[10]
        return round(savings, 2)

    def _get_findings(self, state, avg_cpu, max_cpu, net_in_out, status):
        """Returns finding after checking if EC2 is idle or not."""
        finding = ''
        if status.lower() == 'adhoc':
            finding = 'Adhoc'
        else:
            if state.lower() == 'stopped':
                finding = 'Stopped'
            elif state.lower() == 'running':
                if avg_cpu < self.config['avgCpu'] and max_cpu < self.config['maxCpu'] and net_in_out < self.config['netInOut']: 
                    """ EC2 idle condition check """
                    finding = 'Idle'
        return finding

    def _describe_ec2(self, client):  
        """Returns information of all existing ec2's  in json format."""
        all_instances = client.describe_instances()
        return all_instances['Reservations']

    def _get_ebs_size(self, client, volume_id):  
        """Returns size of the EBS attached."""
        ebs = client.describe_volumes(VolumeIds=[volume_id], )
        size = ebs['Volumes'][0]['Size']
        return float(size)
    
    def _get_clients(self, reg):
        """Fetches and returns clients."""
        client_obj = Client(reg)
        session, cloudwatch_client, pricing_client = client_obj.get_client()
        client = session.client('ec2')
        cloudwatch = CloudwatchUtils(cloudwatch_client)
        pricing = Pricing(pricing_client, reg)
        return client, cloudwatch, pricing

    def _get_parameters(self, instance, reg, client, cloudwatch, pricing, ec2_list):
        """Returns a list containing idle EC2 information."""
        if 'SpotInstanceRequestId' not in instance:
            ec2 = []
            instance_name = vpc_id = instance_os_details = ''
            
            platform_details = self._get_image_info(client, instance['ImageId'])
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'].lower() == 'name':
                        instance_name = tag['Value']

            if 'Platform' not in instance:
                instance_platform = "Linux"
            else:
                instance_platform = instance['Platform']

            if not platform_details:
                if instance_platform == "Linux":
                    instance_os_details = 'Linux/UNIX'
                elif instance_platform == "windows":
                    instance_os_details = 'Windows'
            else:
                instance_os_details = platform_details[0]['PlatformDetails']

            avg_cpu, max_cpu, status = cloudwatch.ec2_get_avg_max_metric('AWS/EC2', 'CPUUtilization',
                                                                            'InstanceId',
                                                                            instance['InstanceId'],
                                                                            self.config)

            network_in = cloudwatch.get_sum_metric('AWS/EC2', 'NetworkIn', 'InstanceId',
                                                    instance['InstanceId'], self.config)
            network_out = cloudwatch.get_sum_metric('AWS/EC2', 'NetworkOut', 'InstanceId',
                                                    instance['InstanceId'], self.config)
            net_in_out = network_out + network_in

            finding = self._get_findings(instance['State']['Name'], avg_cpu, max_cpu, net_in_out,
                                            status)
            
            savings = pricing.get_ec2_price(instance['InstanceType'], instance_os_details)

            if 'VpcId' in instance:
                vpc_id = instance['VpcId']
            if finding == 'Idle':
                #An EC2 is considered idle if it's finding comes out to be 'idle'.
                ec2 = [
                    instance['InstanceId'],
                    instance_name,
                    "EC2",
                    instance['InstanceType'],
                    vpc_id,
                    instance['State']['Name'],
                    reg,
                    finding,
                    self.config['cloudwatch_metrics_period'],
                    f"Average CPUUtilization < {self.config['avgCpu']} Maximum CPUUtilization < {self.config['maxCpu']} and NetworkIn+NetworkOut < {self.config['netInOut']}",
                    round(savings * 732, 2)
                   ]
                ec2_list.append(ec2)            
        return ec2_list

    def get_result(self):  
        """Returns a list of lists which contains headings and idle EC2 information."""
        try:
            ec2_list = []
            headers=[   'ResourceID','ResouceName','ServiceName','Type','VPC',
                        'State','Region','Finding','EvaluationPeriod (seconds)','Criteria','Saving($)'
                    ]
            for reg in self.regions:
                client, cloudwatch, pricing = self._get_clients(reg)
                for r in self._describe_ec2(client):
                        for instance in r['Instances']:
                            ec2_list = self._get_parameters(instance,reg, client, cloudwatch, pricing, ec2_list)

            #To fetch top 10 resources with maximum saving.
            ec2_sorted_list = sorted(ec2_list, key=lambda x: x[10], reverse=True)
            total_savings = self._get_savings(ec2_sorted_list)
            return {'resource_list': ec2_sorted_list, 'headers': headers, 'savings': total_savings}

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in ec2.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in ec2.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " + str(e))
            sys.exit(1)