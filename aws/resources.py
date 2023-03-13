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
from utils.config_parser import parse_config
from utils.utils import get_region_list
from utils.config_parser import merges
class Resources:
   """For making api calls to AWS resources and generating cost report to send on email and slack."""
 
   def __init__(self, config, headers, headers_inventory):
       self.region_list = get_region_list() 
       self.headers = headers
       self.headers_inventory = headers_inventory
       """To get supported regions on an AWS account in list format."""
       self.config=config
       logging.basicConfig(level=logging.WARNING)
       self.logger = logging.getLogger()
 
   def ebs(self): 
       """Function which fetches information resource : EBS."""
       print("Fetching idle resources for EBS")
       ebs_obj = ElasticBlockStore(config=self.config, regions=self.region_list, headers = self.headers, headers_inventory = self.headers_inventory)
       summary, summary_inv = ebs_obj.get_result()
       return summary, summary_inv
 
   def lb(self): 
       """Function which fetches information resource : Loadbalancers."""
       print("Fetching idle resources for LOADBALANCERS")
       lb_obj = Loadbalancer(config=self.config, regions=self.region_list, headers = self.headers, headers_inventory = self.headers_inventory)
       summary, summary_inv = lb_obj.get_result()
       return summary, summary_inv
 
   def rds(self): 
       """Function which fetches information resource : RDS"""
       print("Fetching idle resources for RDS")
       rds_obj = RelationalDatabaseService(config=self.config, regions=self.region_list, headers = self.headers, headers_inventory = self.headers_inventory)
       summary, summary_inv = rds_obj.get_result()
       return summary, summary_inv
 
   def ec2(self): 
       """Function which fetches information resource : EC2"""
       print("Fetching idle resources for EC2")
       ec2_obj = ElasticComputeCloud(config=self.config, regions=self.region_list, headers = self.headers, headers_inventory = self.headers_inventory)
       summary, summary_inv = ec2_obj.get_result()
       return summary, summary_inv
 
   def ec(self): 
       """Function which fetches information resource : Elasticache."""
       print("Fetching idle resources for Elasticache")
       ec_obj = Elasticache(config=self.config, regions=self.region_list, headers = self.headers, headers_inventory = self.headers_inventory)
       summary, summary_inv = ec_obj.get_result()
       return summary, summary_inv
 
   def es(self): 
       """Function which fetches information resource : Elasticsearch."""
       print("Fetching idle resources for Elasticsearch")
       es_obj = Elasticsearch(config=self.config, regions=self.region_list, headers = self.headers, headers_inventory = self.headers_inventory)
       summary, summary_inv = es_obj.get_result()
       return summary, summary_inv
 
   def redshift(self): 
       """Function which fetches information resource : Redshift."""
       print("Fetching idle resources for Redshift")
       rs_obj = Redshift(config=self.config, regions=self.region_list, headers = self.headers, headers_inventory = self.headers_inventory)
       summary, summary_inv = rs_obj.get_result()
       return summary, summary_inv
 
   def eip(self): 
       """Function which fetches information resource : Elastic IP."""
       print("Fetching idle resources for EIP")
       eip_obj = ElasticIP(regions = self.region_list, headers = self.headers, headers_inventory = self.headers_inventory)
       summary, summary_inv = eip_obj.get_result()
       return summary, summary_inv
      
   def get_summary(self, service_name, summary, summary_inv, html_obj, slack_obj, resource_info, inventory_info):
       """Function which fetches the html page and resource information."""
       html_resource=''
       print("Total savings for {} : ${}".format(service_name, summary['savings']))
       if summary['savings'] != 0:
               html_resource = html_obj.get_html_page(service_name, summary['headers'], summary['resource_list'], summary['savings'])
               resource_info = slack_obj.get_resource_list(service_name, resource_info, summary['headers'], summary['resource_list'], summary['savings'])
       inventory_info = slack_obj.get_resource_inventory(service_name, inventory_info, summary_inv['headers_inv'], summary_inv['inv_list'] )
       return html_resource , resource_info, inventory_info
#print("Fetching idle resources for {}".format(service_name))
   def get_report(self, html_obj, slack_obj): 
       """Function which generates cost report to send on email and slack."""
    #    try:
       html = ''
       total_savings = 0
       resource_info = {} #Dictionary which will contain all the information of resources.
       inventory_info = {} #Dictionary which will contain all the information of used resources. 
            
        ###EC2####  
    #    dictionary- resource_list, headers, savings
        # summary, summary_inv = self.ec2()    
        # html_resource , resource_info, inventory_info = self.get_summary('EC2', summary, summary_inv, html_obj, slack_obj, resource_info, inventory_info)
        # total_savings += summary['savings']
        # html += html_resource
        
        ####RDS####
        # summary, summary_inv = self.rds()
        # html_resource , resource_info, inventory_info = self.get_summary('RDS', summary, summary_inv, html_obj, slack_obj, resource_info, inventory_info)
        # total_savings += summary['savings']
        # html += html_resource

        ####LOADBALANCERS####
       summary, summary_inv = self.lb()
       html_resource , resource_info, inventory_info = self.get_summary('LOADBALANCERS', summary, summary_inv, html_obj, slack_obj, resource_info, inventory_info)
       total_savings += summary['savings']
       html += html_resource
    
        ####EBS####
        # summary, summary_inv = self.ebs()
        # html_resource , resource_info, inventory_info = self.get_summary('EBS', summary, summary_inv, html_obj, slack_obj, resource_info, inventory_info)
        # total_savings += summary['savings']
        # html += html_resource

        ####EIP####
        # summary, summary_inv = self.eip()
        # html_resource , resource_info, inventory_info = self.get_summary('EIP', summary, summary_inv, html_obj, slack_obj, resource_info, inventory_info)
        # total_savings += summary['savings']
        # html += html_resource

        ####ELASTICACHE####
        # summary, summary_inv = self.ec()
        # html_resource , resource_info, inventory_info = self.get_summary('ELASTICACHE', summary, summary_inv, html_obj, slack_obj, resource_info, inventory_info)
        # total_savings += summary['savings']
        # html += html_resource

        ###ELASTICSEARCH####
        # summary, summary_inv = self.es()
        # html_resource , resource_info, inventory_info = self.get_summary('ELASTICSEARCH', summary, summary_inv, html_obj, slack_obj, resource_info, inventory_info)
        # total_savings += summary['savings']
        # html += html_resource

        ####REDSHIFT####
        # summary, summary_inv = self.redshift()
        # html_resource , resource_info, inventory_info = self.get_summary('REDSHIFT', summary, summary_inv, html_obj, slack_obj, resource_info, inventory_info)
        # total_savings += summary['savings']
        # html += html_resource

        ####FINAL HTML PAGE GENERATION####
       html_prefix = html_obj.get_HTML_prefix()
       html_suffix = html_obj.get_HTML_suffix()
       html = html_prefix + html + html_suffix
       return html, resource_info, total_savings, inventory_info

    #    except Exception as e:
    #        self.logger.error("Error on line {} in resources.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
    #                          str(e))
    #        sys.exit(1)
