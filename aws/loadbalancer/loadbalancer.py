import logging
from botocore import exceptions
import sys
from aws.loadbalancer.pricing import Pricing
from utils.client import CLIENT
from utils.cloudwatch_utils import CLOUDWATCH_UTILS


class LOADBALANCER:
    '''To fetch information of all idle Loadbalancers'''
    def __init__(self, config=None, regions=None):
        self.config = config['LB']
        self.regions = regions
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _describe_classic_lb(self, client):             # Returns information of classic loadbalancers in json format
        classic_lbs = client.describe_load_balancers()
        return classic_lbs['LoadBalancerDescriptions']

    def _describe_lb(self, elbv2_client):     # Returns information of application/network loadbalancers in json format
        lbs = elbv2_client.describe_load_balancers()
        return lbs['LoadBalancers']

    def _get_lb_price(self, pricing_client, region):
        pricing = Pricing(pricing_client, region)
        elb_price = pricing.get_lb_price('Load Balancer')
        alb_price = pricing.get_lb_price('Load Balancer-Application')
        nlb_price = pricing.get_lb_price('Load Balancer-Network')
        return elb_price, alb_price, nlb_price

    def _get_savings(self, lb_list):    # Returns total possible savings
        savings = 0
        for lb in lb_list:
            savings = savings + lb[6]
        return round(savings, 2)

    def get_result(self):  # Returns a list of lists which contains headings and idle loadbalancers information
        try:
            lb_list = []
            headers = ['LoadBalancerName', 'Type', 'CreationDate', 'AWSRegion', 'MonthlyCost($)', 'Finding',
                       'Savings($)']
            for reg in self.regions:
                client_obj = CLIENT(reg)
                session, cloudwatch_client, pricing_client = client_obj.get_client()
                client = session.client('elb')
                elbv2_client = session.client('elbv2')
                elb_price, alb_price, nlb_price = self._get_lb_price(pricing_client, reg)

                for elb in self._describe_classic_lb(client):
                    classic_lb = []
                    cloudwatch = CLOUDWATCH_UTILS(cloudwatch_client)
                    connection_count = cloudwatch.get_sum_metric('AWS/ELB', 'RequestCount',
                                                                 'LoadBalancerName', elb['LoadBalancerName'],
                                                                 self.config)
                    if connection_count < 1:      # Idle loadbalancer check
                        finding = 'Idle'
                    else:
                        finding = 'ClassicLB'

                    classic_lb.append(elb['LoadBalancerName'])
                    classic_lb.append('Classic')
                    classic_lb.append(elb['CreatedTime'].date())
                    classic_lb.append(reg)
                    classic_lb.append(round(elb_price, 2))
                    classic_lb.append(finding)
                    if finding == 'Idle':
                        classic_lb.append(round(elb_price, 2))
                    else:
                        classic_lb.append(round(elb_price - alb_price, 2))
                    lb_list.append(classic_lb)

                for lb in self._describe_lb(elbv2_client):
                    nlb_albs = []
                    cloudwatch = CLOUDWATCH_UTILS(cloudwatch_client)
                    finding = namespace = metric_name = ''
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
                    if connection_count < 1:  # Idle loadbalancer check
                        finding = 'Idle'

                    if finding == 'Idle':
                        nlb_albs.append(lb['LoadBalancerName'])
                        nlb_albs.append(lb['Type'])
                        nlb_albs.append(lb['CreatedTime'].date())
                        nlb_albs.append(reg)
                        nlb_albs.append(round(price, 2))
                        nlb_albs.append(finding)
                        nlb_albs.append(round(price, 2))
                        lb_list.append(nlb_albs)
            # To fetch top 10 resources with maximum saving
            lb_sorted_list = sorted(lb_list, key=lambda x: x[6], reverse=True)
            total_savings = self._get_savings(lb_sorted_list)
            return lb_sorted_list, headers, total_savings

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in loadbalancer.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in loadbalancer.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)
