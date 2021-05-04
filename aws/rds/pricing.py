import logging
from botocore import exceptions
import sys
import json
from utils.utils import get_region_name, get_price, get_price1

# Filters for get_products pricing api call used to fetch RDS price
rds_filter = '[{{"Field": "databaseEngine", "Value": "{e}", "Type": "TERM_MATCH"}},' \
             '{{"Field": "instanceType", "Value": "{i}", "Type": "TERM_MATCH"}},' \
             '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
             '{{"Field": "deploymentOption", "Value": "{d}", "Type": "TERM_MATCH"}}]'

rds_filter_oracle_mysql = '[{{"Field": "databaseEngine", "Value": "{e}", "Type": "TERM_MATCH"}},' \
                          '{{"Field": "instanceType", "Value": "{i}", "Type": "TERM_MATCH"}},' \
                          '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
                          '{{"Field": "licenseModel", "Value": "{lm}", "Type": "TERM_MATCH"}},' \
                          '{{"Field": "deploymentOption", "Value": "{d}", "Type": "TERM_MATCH"}},' \
                          '{{"Field": "databaseEdition", "Value": "{de}", "Type": "TERM_MATCH"}}]'

rds_storage = '[{{"Field": "volumeType", "Value": "{v}", "Type": "TERM_MATCH"}},' \
              '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
              '{{"Field": "deploymentOption", "Value": "{d}", "Type": "TERM_MATCH"}}]'

rds_iops = '[{{"Field": "productFamily", "Value": "Provisioned IOPS", "Type": "TERM_MATCH"}},' \
           '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
           '{{"Field": "deploymentOption", "Value": "{d}", "Type": "TERM_MATCH"}}]'


class Pricing:
    '''For getting and returning the price of the RDS'''

    def __init__(self, pricing_client=None, region=None):
        self.pricing_client = pricing_client
        self.region = region
        self.formatted_region = get_region_name(region)
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def _get_rds_engine(self, engine): # Returns RDS engine
        db_engine_mapping = {'mysql': 'MySQL', 'postgres': 'PostgreSQL', 'mariadb': 'MariaDB',
                             'aurora-postgresql': 'Aurora PostgreSQL', 'aurora-mysql': 'Aurora MySQL',
                             'aurora': 'Aurora MySQL',
                             'oracle-ee': 'Oracle', 'oracle-se': 'Oracle', 'oracle-se1': 'Oracle',
                             'oracle-se2': 'Oracle',
                             'sqlserver-ee': 'SQL Server', 'sqlserver-se': 'SQL Server', 'sqlserver-ex': 'SQL Server',
                             'sqlserver-web': 'SQL Server'}
        return db_engine_mapping.get(engine)

    def _get_rds_edition(self, engine): # Returns RDS edition
        db_edition_mapping = {'oracle-ee': 'Enterprise', 'oracle-se': 'Standard', 'oracle-se1': 'Standard One',
                              'oracle-se2': 'Standard Two', 'sqlserver-ee': 'Enterprise', 'sqlserver-se': 'Standard',
                              'sqlserver-ex': 'Express', 'sqlserver-web': 'Web'}
        return db_edition_mapping.get(engine)

    def _get_rds_volume(self, storage): # Returns RDS volume information
        db_storage_mapping = {'gp2': 'General Purpose', 'io1': 'Provisioned IOPS', 'aurora': 'General Purpose-Aurora',
                              'standard': 'Magnetic'}
        return db_storage_mapping.get(storage)

    def get_rds_price(self, db_engine_identifier, db_instance, multi_az, db_license, storage_type, allocated_storage,
                      iops):  # Returns RDS Price
        try:
            license_model = 'License included'
            if db_license == 'bring-your-own-license':
                license_model = 'Bring your own license'
            deployment_option = 'Single-AZ'
            if multi_az:
                deployment_option = 'Multi-AZ'
            db_engine = self._get_rds_engine(db_engine_identifier)
            db_volume = self._get_rds_volume(storage_type)
            if 'SQL Server' in db_engine or 'Oracle' in db_engine:
                db_edition = self._get_rds_edition(db_engine_identifier)
                f = rds_filter_oracle_mysql.format(r=self.formatted_region, i=db_instance, e=db_engine,
                                                   d=deployment_option, de=db_edition, lm=license_model)
            else:
                f = rds_filter.format(r=self.formatted_region, i=db_instance, e=db_engine, d=deployment_option)
            instance_data = self.pricing_client.get_products(ServiceCode='AmazonRDS', Filters=json.loads(f))
            instance_price = get_price1(instance_data)
            f = rds_storage.format(r=self.formatted_region, d=deployment_option, v=db_volume)
            volume_data = self.pricing_client.get_products(ServiceCode='AmazonRDS', Filters=json.loads(f))
            volume_price = get_price(volume_data) * allocated_storage
            iops_price = 0
            if iops != 0:
                f = rds_iops.format(r=self.formatted_region, d=deployment_option)
                iops_data = self.pricing_client.get_products(ServiceCode='AmazonRDS', Filters=json.loads(f))
                iops_price = get_price(iops_data) * iops

            storage_price = volume_price + iops_price
            return float(instance_price), float(storage_price)

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in rds pricing.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error("Error on line {} in rds pricing.py".format(sys.exc_info()[-1].tb_lineno) +
                              " | Message: " + str(e))
            sys.exit(1)
