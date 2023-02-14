import logging
from botocore import exceptions
import sys
from aws.loadbalancer.pricing import Pricing
from utils.client import Client
from utils.cloudwatch_utils import CloudwatchUtils
from utils.utils import handle_limit_exceeded_exception


class Loadbalancer:
    """To fetch information of all idle Loadbalancers."""
    def __init__(self, headers, headers_inventory, config=None, regions=None):
        try:
         self.config = config.get('LB')
         self.headers = headers
         self.headers_inventory = headers_inventory
        except KeyError as e:
            self.logger.error(
                "Config for LB missing from config.cfg | Message: " + str(e))       
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_classic_lb(self, client):   
        """Returns information of classic loadbalancers in json format."""
        classic_lbs = client.describe_load_balancers()
        print("+++++++++++++details of classic loadbalancer +++++++++++++++++++++++")
        print(classic_lbs)
        print("[[[[[[[[[[[[[[[[[[[")
        print(classic_lbs['LoadBalancerDescriptions'])
        return classic_lbs['LoadBalancerDescriptions']

    def _describe_lb(self, elbv2_client):     
        """Returns information of application/network loadbalancers in json format."""
        lbs = elbv2_client.describe_load_balancers()
        return lbs['LoadBalancers']

    def _get_lb_price(self, pricing_client, region):
        pricing = Pricing(pricing_client, region)
        elb_price = pricing.get_lb_price('Load Balancer')
        alb_price = pricing.get_lb_price('Load Balancer-Application')
        nlb_price = pricing.get_lb_price('Load Balancer-Network')
        return elb_price, alb_price, nlb_price

    def _get_savings(self, lb_list):    
        """Returns total possible savings."""
        savings = 0
        for lb in lb_list:
            savings = savings + lb[10]
        return round(savings, 2)

    def _get_clients(self, reg):
        """Fetches and returns clients."""
        client_obj = Client(reg)
        session, cloudwatch_client, pricing_client = client_obj.get_client()
        client = session.client('elb')
        cloudwatch = CloudwatchUtils(cloudwatch_client)
        elbv2_client = session.client('elbv2')
        return client, cloudwatch, elbv2_client, pricing_client

    def _get_clb_parameters(self, elb, reg, cloudwatch, elb_price, alb_price, lb_list, lb_inv_list):
        """Returns list containing idle loadbalancers information."""
        print("============lb_list==========")
        print(lb_list)
        print("============lb_inv_lis==========")
        print(lb_inv_list)
        print("============elb===========")
        print(elb)
        print("==================reg===========")
        print(reg)
        print("============elb_price===============")
        print(elb_price)
        print("==================alb_price=============")
        print(alb_price)
        classic_lb = []        
        connection_count = cloudwatch.get_sum_metric('AWS/ELB', 'RequestCount',
                                                        'LoadBalancerName', elb['LoadBalancerName'],
                                                        self.config)
        #Idle loadbalancer check.
        if connection_count < self.config['connectionCount']:      
            finding = 'Idle'
        else:
            finding = 'ClassicLB'
        classic_lb = [
            elb['LoadBalancerName'],
            elb['LoadBalancerName'],
            "LOADBALANCER",
            'Classic',
            elb['VpcId'],
            "-",
            reg,
            finding,
            self.config['cloudwatch_metrics_period'],
            f"RequestCount < {self.config['connectionCount']}",
            round(elb_price, 2),
            ]
        if finding == 'Idle':
            classic_lb.append(round(elb_price, 2))
        else:
            classic_lb.append(round(elb_price - alb_price, 2))
        
        lb_list.append(classic_lb)
        clb_inv = [
            elb['LoadBalancerName'],
            elb['LoadBalancerName'],
            "LOADBALANCER",
            'Classic',
            elb['VpcId'],
            '-',
            reg,
            'Yes'
            ]
        lb_inv_list.append(clb_inv)
        return lb_list, lb_inv_list
    
    def _get_lb_parameters(self, lb, reg, cloudwatch, alb_price, nlb_price, lb_list, lb_inv_list):
        """Returns a list containing idle loadbalancers information."""
        
        nlb_albs = []
        finding = namespace = metric_name = ''
        is_idle = 'No'
        price = 0
        lb_arn = lb['LoadBalancerArn'].split('/', 1)[1]
        if lb['Type'] == 'network':
            namespace = 'AWS/NetworkELB'    
            metric_name = 'ActiveFlowCount'
            price = nlb_price
        if lb['Type'] == 'application':
            namespace = 'AWS/ApplicationELB'
            metric_name = 'RequestCount'
            price = alb_price
        connection_count = cloudwatch.get_sum_metric(namespace, metric_name,
                                                    'LoadBalancer', lb_arn, self.config)
        #Idle loadbalancer check.
        if connection_count < self.config['connectionCount']:  
            finding = 'Idle'

        if finding == 'Idle':
            is_idle = 'Yes'
            nlb_albs =[
            lb['LoadBalancerName'],
            lb['LoadBalancerName'],
            "LOADBALANCER",
            lb['Type'],
            lb['VpcId'],
            lb['State']['Code'],
            reg,
            finding,
            self.config['cloudwatch_metrics_period'],
            f"{metric_name} < {self.config['connectionCount']}",
            round(price, 2)
            ]
            lb_list.append(nlb_albs)
            
        nlb_albs_inv =[
            lb['LoadBalancerName'],
            lb['LoadBalancerName'],
            "LOADBALANCER",
            lb['Type'],
            lb['VpcId'],
            lb['State']['Code'],
            reg,
            is_idle
            ]
        lb_inv_list.append(nlb_albs_inv)
            
        return lb_list, lb_inv_list

    def get_result(self):  
        """Returns a list of lists which contains headings and idle loadbalancers information."""
        try:
            lb_list = []
            lb_inv_list = []

            for reg in self.regions:
                client, cloudwatch, elbv2_client, pricing_client = self._get_clients(reg)
                elb_price, alb_price, nlb_price = self._get_lb_price(pricing_client, reg)

                for elb in self._describe_classic_lb(client):
                    lb_list, lb_inv_list = self._get_clb_parameters(elb, reg, cloudwatch, elb_price, alb_price, lb_list, lb_inv_list)
                for lb in self._describe_lb(elbv2_client):
                    lb_list, lb_inv_list = self._get_lb_parameters(lb, reg, cloudwatch, alb_price, nlb_price, lb_list, lb_inv_list)

            #To fetch top 10 resources with maximum saving.
            lb_sorted_list = sorted(lb_list, key=lambda x: x[10], reverse=True)
            total_savings = self._get_savings(lb_sorted_list)
            return {'resource_list': lb_sorted_list, 'headers': self.headers, 'savings': total_savings}, {'headers_inv': self.headers_inventory, 'inv_list': lb_inv_list}
            
        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'loadbalancer.py')
            sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in loadbalancer.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)
