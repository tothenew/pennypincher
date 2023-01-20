import sys
import logging
from botocore import exceptions
import json
from utils.utils import get_region_name, get_price
from utils.utils import handle_limit_exceeded_exception

class Pricing:
    """For getting and returning the price of the EBS volumes."""
    
    #Filter for get_products pricing api call used to fetch EC2 price.
    ec2_filter = '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},' \
                '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},' \
                '{{"Field": "preInstalledSw", "Value": "{s}", "Type": "TERM_MATCH"}},' \
                '{{"Field": "instanceType", "Value": "{t}", "Type": "TERM_MATCH"}},' \
                '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
                '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}},' \
                '{{"Field": "licenseModel", "Value": "{l}", "Type": "TERM_MATCH"}}]'



    def __init__(self, pricing_client=None, region=None):
        self.pricing_client = pricing_client
        self.region = region
        self.formatted_region = get_region_name(region)
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()


    def get_os(self, os):  
        """Returns OS of the AMI used in EC2."""
        try:
            os_mapping = {'Linux/UNIX': 'Linux', 'SQL Server Standard': 'Linux', 'SQL Server Web': 'Linux',
                          'SQL Server Enterprise': 'Linux', 'Red Hat Enterprise Linux': 'RHEL',
                          'SUSE Linux': 'SUSE', 'Windows': 'Windows', 'Windows BYOL': 'Windows',
                          'Windows with SQL Server Standard': 'Windows', 'Windows with SQL Server Web': 'Windows',
                          'Windows with SQL Server Enterprise': 'Windows'
                          }
            return os_mapping.get(os, os)
        except Exception as e:
            self.logger.error("Error on line {} in ec2 pricing.py".format(sys.exc_info()[-1].tb_lineno) +
                              " Message: " + str(e))
            raise e
            sys.exit(1)

    def get_preinstalled_sw(self, os):  
        """Returns pre installed software information in AMI used in EC2."""
        try:
            sw_mapping = {'Linux/UNIX': 'NA', 'SQL Server Standard': 'SQL Std', 'SQL Server Web': 'SQL Web',
                          'SQL Server Enterprise': 'SQL Ent', 'Windows': 'NA',
                          'Windows with SQL Server Enterprise': 'SQL Ent',
                          'Windows with SQL Server Standard': 'SQL Std', 'Windows with SQL Server Web': 'SQL Web',
                          'Red Hat Enterprise Linux': 'NA'}
            return sw_mapping.get(os, os)
        except Exception as e:
            self.logger.error("Error on line {} in ec2 pricing.py".format(sys.exc_info()[-1].tb_lineno) +
                              " Message: " + str(e))
            raise e
            sys.exit(1)

    def get_license(self, os):  
        """Returns license information of EC2 AMI."""
        try:
            license_mapping = {'Windows BYOL': 'Bring your own license'
                               }
            return license_mapping.get(os, 'No License required')

        except Exception as e:          
            self.logger.error("Error on line {} in ec2 pricing.py".format(sys.exc_info()[-1].tb_lineno) +
                              " Message: " + str(e))
            raise e
            #check for sys.exit(1), if code breaks
            sys.exit(1)

    def get_ec2_price(self, instance_type, operating_system):  
        """Returns the price of EC2."""
        try:
            os = self.get_os(operating_system)
            lic = self.get_license(operating_system)
            software = self.get_preinstalled_sw(operating_system)
            f = self.ec2_filter.format(r=self.formatted_region, t=instance_type, o=os, l=lic, s=software)
            data = self.pricing_client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
            ondemand_price = get_price(data)
            return float(ondemand_price)

        except exceptions.ClientError as error:
            handle_limit_exceeded_exception(error, 'ec2 pricing.py')
            sys.exit(1)
        except Exception as e:
            self.logger.error("Error on line {} in ec2 pricing.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: "
                              + str(e))
            # sys.exit(1)
