import logging
import sys
from aws.ebs.ebs import EBS
from aws.eip.eip import EIP
from aws.rds.rds import RDS
from aws.ec2.ec2 import EC2
from aws.redshift.redshift import REDSHIFT
from aws.elasticache.elasticache import ELASTICACHE
from aws.loadbalancer.loadbalancer import LOADBALANCER
from aws.elasticsearch.elasticsearch import ELASTICSEARCH
from utils.config_parser import CONFIGPARSER
from utils.utils import get_region_list


class RESOURCES:
    ''' For making api calls to AWS resources and generating cost report to send on email and slack'''

    def __init__(self, config):
        self.region_list = get_region_list()  # To get supported regions on an AWS account in list format
        cfg_obj = CONFIGPARSER(config)  # For fetching configuration for cloudwatch from .cfg file
        self.config = cfg_obj.get_config()
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def ebs(self):  # Function which fetches information resource : EBS
        ebs_obj = EBS(self.config, self.region_list)
        ebs_list, headers, savings = ebs_obj.get_result()
        return ebs_list, headers, savings

    def lb(self):  # Function which fetches information resource : Loadbalancers
        lb_obj = LOADBALANCER(self.config, self.region_list)
        lb_list, headers, savings = lb_obj.get_result()
        return lb_list, headers, savings

    def rds(self):  # Function which fetches information resource : RDS
        rds_obj = RDS(self.config, self.region_list)
        rds_list, headers, savings = rds_obj.get_result()
        return rds_list, headers, savings

    def ec2(self):  # Function which fetches information resource : EC2
        ec2_obj = EC2(self.config, self.region_list)
        ec2_list, headers, savings = ec2_obj.get_result()
        return ec2_list, headers, savings

    def ec(self):  # Function which fetches information resource : Elasticache
        ec_obj = ELASTICACHE(self.config, self.region_list)
        ec_list, headers, savings = ec_obj.get_result()
        return ec_list, headers, savings

    def es(self):  # Function which fetches information resource : Elasticsearch
        es_obj = ELASTICSEARCH(self.config, self.region_list)
        es_list, headers, savings = es_obj.get_result()
        return es_list, headers, savings

    def redshift(self):  # Function which fetches information resource : Redshift
        rs_obj = REDSHIFT(self.config, self.region_list)
        rs_list, headers, savings = rs_obj.get_result()
        return rs_list, headers, savings

    def eip(self):  # Function which fetches information resource : Elastic IP
        eip_obj = EIP(self.config, self.region_list)
        eip_list, headers, savings = eip_obj.get_result()
        return eip_list, headers, savings

    def get_report(self, html_obj, slack_obj):  # Function which generates cost report to send on email and slack
        try:
            html_ebs = html_rds = html_lb = html_ec2 = html_ec = html_es = html_rs = html_eip = ''
            resource_info = {}  # Dictionary which will contain all the information of resources

            ########## EC2 ############
            ec2_list, ec2_header, ec2_savings = self.ec2()
            if ec2_savings != 0:
                html_ec2 = html_obj.get_html_page('EC2', ec2_header, ec2_list, ec2_savings)
                resource_info = slack_obj.get_resource_list('EC2', resource_info, ec2_header, ec2_list, ec2_savings)

            ########## RDS ############
            rds_list, rds_header, rds_savings = self.rds()
            if rds_savings != 0:
                html_rds = html_obj.get_html_page('RDS', rds_header, rds_list, rds_savings)
                resource_info = slack_obj.get_resource_list('RDS', resource_info, rds_header, rds_list, rds_savings)

            ########## LOADBALANCERS ############
            lb_list, lb_header, lb_savings = self.lb()
            if lb_savings != 0:
                html_lb = html_obj.get_html_page('LOADBALANCERS', lb_header, lb_list, lb_savings)
                resource_info = slack_obj.get_resource_list('LOADBALANCERS', resource_info, lb_header, lb_list,
                                                            lb_savings)

            ########## EBS ############
            ebs_list, ebs_header, ebs_savings = self.ebs()
            if ebs_savings != 0:
                html_ebs = html_obj.get_html_page('EBS', ebs_header, ebs_list, ebs_savings)
                resource_info = slack_obj.get_resource_list('EBS', resource_info, ebs_header, ebs_list, ebs_savings)

            ########## EIP ############
            eip_list, eip_header, eip_savings = self.eip()
            if eip_savings != 0:
                html_eip = html_obj.get_html_page('EIP', eip_header, eip_list, eip_savings)
                resource_info = slack_obj.get_resource_list('EIP', resource_info, eip_header, eip_list, eip_savings)

            ########## ELASTICACHE ############
            ec_list, ec_header, ec_savings = self.ec()
            if ec_savings != 0:
                html_ec = html_obj.get_html_page('ELASTICACHE', ec_header, ec_list, ec_savings)
                resource_info = slack_obj.get_resource_list('ELASTICACHE', resource_info, ec_header, ec_list,
                                                            ec_savings)

            ########## ELASTICSEARCH ############
            es_list, es_header, es_savings = self.es()
            if es_savings != 0:
                html_es = html_obj.get_html_page('ELASTICSEARCH', es_header, es_list, es_savings)
                resource_info = slack_obj.get_resource_list('ELASTICSEARCH', resource_info, es_header, es_list,
                                                            es_savings)

            ########## REDSHIFT ############
            rs_list, rs_header, rs_savings = self.redshift()
            if rs_savings != 0:
                html_rs = html_obj.get_html_page('REDSHIFT', rs_header, rs_list, rs_savings)
                resource_info = slack_obj.get_resource_list('REDSHIFT', resource_info, rs_header, rs_list, rs_savings)

            ########## FINAL HTML PAGE GENERATION##########
            html_prefix = html_obj.get_HTML_prefix()
            html_suffix = html_obj.get_HTML_suffix()
            html = html_prefix + html_ec2 + html_rds + html_lb + html_ebs + html_eip + html_ec + html_es + html_rs + \
                   html_suffix

            total_savings = ec2_savings + rds_savings + ebs_savings + eip_savings + lb_savings + \
                        rs_savings + ec_savings + es_savings
            return html, resource_info, total_savings

        except Exception as e:
            self.logger.error("Error on line {} in resources.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                              str(e))
            sys.exit(1)
