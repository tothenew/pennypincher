import logging
import sys
from aws.ebs.ebs import ElasticBlockStore
from aws.eip.eip import ElasticIP
from aws.rds.rds import RelationalDatabaseService
from aws.ec2.ec2 import ElasticComputeCloud
from aws.redshift.redshift import Redshift
from aws.elasticache.elasticache import Elasticache
from aws.loadbalancer.loadbalancer import Loadbalancer
from aws.elasticsearch.elasticsearch import Elasticsearch
from utils.config_parser import CONFIGPARSER
from utils.utils import get_region_list
 
 
class Resources:
   """For making api calls to AWS resources and generating cost report to send on email and slack."""
 
   def __init__(self, config):
       self.region_list = get_region_list() 
       """To get supported regions on an AWS account in list format."""
       cfg_obj = CONFIGPARSER(config) 
       #For fetching configuration for cloudwatch from .cfg file.
       self.config = cfg_obj.get_config()
       logging.basicConfig(level=logging.WARNING)
       self.logger = logging.getLogger()
 
   def ebs(self): 
       """Function which fetches information resource : EBS."""
       print("Fetching idle resources for EBS")
       ebs_obj = ElasticBlockStore(self.config, self.region_list)
       summary = ebs_obj.get_result()
       return summary
 
   def lb(self): 
       """Function which fetches information resource : Loadbalancers."""
       print("Fetching idle resources for LOABALANCERS")
       lb_obj = Loadbalancer(self.config, self.region_list)
       summary = lb_obj.get_result()
       return summary
 
   def rds(self): 
       """Function which fetches information resource : RDS"""
       print("Fetching idle resources for RDS")
       rds_obj = RelationalDatabaseService(self.config, self.region_list)
       summary = rds_obj.get_result()
       return summary
 
   def ec2(self): 
       """Function which fetches information resource : EC2"""
       print("Fetching idle resources for EC2")
       ec2_obj = ElasticComputeCloud(self.config, self.region_list)
       summary = ec2_obj.get_result()
       return summary
 
   def ec(self): 
       """Function which fetches information resource : Elasticache."""
       print("Fetching idle resources for Elasticache")
       ec_obj = Elasticache(self.config, self.region_list)
       summary = ec_obj.get_result()
       return summary
 
   def es(self): 
       """Function which fetches information resource : Elasticsearch."""
       print("Fetching idle resources for Elasticsearch")
       es_obj = Elasticsearch(self.config, self.region_list)
       summary = es_obj.get_result()
       return summary
 
   def redshift(self): 
       """Function which fetches information resource : Redshift."""
       print("Fetching idle resources for Redshift")
       rs_obj = Redshift(self.config, self.region_list)
       summary = rs_obj.get_result()
       return summary
 
   def eip(self): 
       """Function which fetches information resource : Elastic IP."""
       print("Fetching idle resources for EIP")
       eip_obj = ElasticIP(self.region_list)
       summary = eip_obj.get_result()
       return summary
      
   def get_summary(self, service_name, summary, html_obj, slack_obj, resource_info):
       """Function which fetches the html page and resource information."""
       html_resource=''
       print("Total savings for {} : ${}".format(service_name, summary['savings']))
       if summary['savings'] != 0:
               html_resource = html_obj.get_html_page(service_name, summary['headers'], summary['resource_list'], summary['savings'])
               resource_info = slack_obj.get_resource_list(service_name, resource_info, summary['headers'], summary['resource_list'], summary['savings'])
       return html_resource , resource_info
#print("Fetching idle resources for {}".format(service_name))
   def get_report(self, html_obj, slack_obj): 
       """Function which generates cost report to send on email and slack."""
       try:
           html = ''
           total_savings = 0
           resource_info = {} #Dictionary which will contain all the information of resources. 
          
           ####EC2####  
           # dictionary- resource_list, headers, savings
           summary = self.ec2()    
           html_resource , resource_info = self.get_summary('EC2', summary, html_obj, slack_obj, resource_info)
           total_savings += summary['savings']
           html += html_resource
          
        #    ####RDS####
        #    summary = self.rds()
        #    html_resource, resource_info = self.get_summary('RDS', summary, html_obj, slack_obj, resource_info)
        #    total_savings += summary['savings']
        #    html += html_resource
 
        #    ####LOADBALANCERS####
        #    summary = self.lb()
        #    html_resource , resource_info = self.get_summary('LOADBALANCERS', summary, html_obj, slack_obj, resource_info)
        #    total_savings += summary['savings']
        #    html += html_resource
        #    ####EBS####
        #    summary = self.ebs()
        #    html_resource , resource_info = self.get_summary('EBS', summary, html_obj, slack_obj, resource_info)
        #    total_savings += summary['savings']
        #    html += html_resource
 
        #    ####EIP####
        #    summary = self.eip()
        #    html_resource , resource_info = self.get_summary('EIP', summary, html_obj, slack_obj, resource_info)
        #    total_savings += summary['savings']
        #    html += html_resource
 
        #    ####ELASTICACHE####
        #    summary = self.ec()
        #    html_resource , resource_info = self.get_summary('ELASTICACHE', summary, html_obj, slack_obj, resource_info)
        #    total_savings += summary['savings']
        #    html += html_resource
 
        #    ####ELASTICSEARCH####
        #    summary = self.es()
        #    html_resource , resource_info = self.get_summary('ELASTICSEARCH', summary, html_obj, slack_obj, resource_info)
        #    total_savings += summary['savings']
        #    html += html_resource
 
        #    ####REDSHIFT####
        #    summary = self.redshift()
        #    html_resource , resource_info = self.get_summary('REDSHIFT', summary, html_obj, slack_obj, resource_info)
        #    total_savings += summary['savings']
        #    html += html_resource
 
        #    ####FINAL HTML PAGE GENERATION####
        #    html_prefix = html_obj.get_HTML_prefix()
        #    html_suffix = html_obj.get_HTML_suffix()
        #    html = html_prefix + html + html_suffix
           return html, resource_info, total_savings
 
       except Exception as e:
           self.logger.error("Error on line {} in resources.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                             str(e))
           sys.exit(1)
