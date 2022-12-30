import datetime
from datetime import timezone
import json
import boto3
import math
import logging
import sys


def get_normalization_factor(instance_type):
    type = instance_type.split(".")[1]
    normalization_factor_mapping = {'nano': 0.25, 'micro': 0.5, 'small': 1, 'medium': 2, 'large': 4, 'xlarge': 8,
                                    '2xlarge': 16, '4xlarge': 32, '8xlarge': 64, '9xlarge': 72, '10xlarge': 80,
                                    '12xlarge': 96, '16xlarge': 128, '24xlarge': 192, '32xlarge': 256}
    return float(normalization_factor_mapping.get(type))


def convert_size(size_in_bytes):   
    """Returns size in a human readable format."""
    if size_in_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_in_bytes, 1024)))
    power = math.pow(1024, i)
    size = round(size_in_bytes / power, 2)
    return "{} {}".format(size, size_name[i])


def get_region_name(region_code):  
    """Returns region name corresponding to the region abbreviation."""
    try:
        region_mapping = {'us-east-1': 'US East (N. Virginia)', 'us-east-2': 'US East (Ohio)',
                          'us-west-1': 'US West (N. California)', 'us-west-2': 'US West (Oregon)',
                          'af-south-1': 'Africa (Cape Town)',
                          'ap-northeast-1': 'Asia Pacific (Tokyo)', 'ap-northeast-2': 'Asia Pacific (Seoul)',
                          'ap-northeast-3': 'Asia Pacific (Osaka)',
                          'ap-southeast-1': 'Asia Pacific (Singapore)', 'ap-southeast-2': 'Asia Pacific (Sydney)',
                          'ap-east-1': 'Asia Pacific (Hong Kong)',
                          'ap-south-1': 'Asia Pacific (Mumbai)',
                          'ca-central-1': 'Canada (Central)',
                          'eu-central-1': 'EU (Frankfurt)',
                          'eu-west-1': 'EU (Ireland)', 'eu-west-2': 'EU (London)', 'eu-west-3': 'EU (Paris)',
                          'eu-north-1': 'EU (Stockholm)',
                          'eu-south-1': 'EU (Milan)',
                          'me-south-1': 'Middle East (Bahrain)',
                          'sa-east-1': 'South America (Sao Paulo)',
                          }
        return region_mapping.get(region_code)
    except Exception as e:
        return 'US East (N. Virginia)'


def get_region_list():   
    """Returns a list of valid regions for an AWS account."""
    try:
        regions = []
        ec2 = boto3.client('ec2')
        response = ec2.describe_regions()
        for reg in response['Regions']:
            regions.append(reg['RegionName'])
        return regions
    except Exception as e:
        return 'us-east-1'


def get_backup_age(creation_date):   
    """Returns age of the backup."""
    today = datetime.datetime.now(timezone.utc).date()
    delta = today - creation_date
    return delta.days


def get_region_code(region_code):   
    """Returns region code corresponding to an AWS region abbreviation."""
    try:
        region_mapping = {'us-east-1': 'USE1', 'us-east-2': 'USE2',
                          'us-west-1': 'USW1', 'us-west-2': 'USW2',
                          'af-south-1': 'CPT',
                          'ap-northeast-1': 'APN1', 'ap-northeast-2': 'APN2',
                          'ap-northeast-3': 'APN3',
                          'ap-southeast-1': 'APS1', 'ap-southeast-2': 'APS2',
                          'ap-east-1': 'APE1',
                          'ap-south-1': 'APS3',
                          'ca-central-1': 'CAN1',
                          'eu-central-1': 'EUC1',
                          'eu-west-1': 'EU', 'eu-west-2': 'EUW2', 'eu-west-3': 'EUW3',
                          'eu-north-1': 'EUN1',
                          'me-south-1': 'MES1',
                          'sa-east-1': 'SAE1',
                          }
        return region_mapping.get(region_code)
    except Exception as e:
        return 'USE1'


def get_price(data):   
    """Fetches and returns price from pricing api json."""
    od = json.loads(data['PriceList'][0])['terms']['OnDemand']
    id1 = list(od)[0]
    id2 = list(od[id1]['priceDimensions'])[0]
    price = float(od[id1]['priceDimensions'][id2]['pricePerUnit']['USD'])
    return price


def get_price1(data):  
    """Fetches and returns price from pricing api json."""
    od = json.loads(data['PriceList'][0])['terms']['OnDemand']
    id1 = list(od)[0]
    id2 = list(od[id1]['priceDimensions'])[0]
    price = float(od[id1]['priceDimensions'][id2]['pricePerUnit']['USD'])
    return price * 732


def get_price2(data):  
    """Fetches and returns price from pricing api json."""
    od = json.loads(data['PriceList'][1])['terms']['OnDemand']
    id1 = list(od)[0]
    id2 = list(od[id1]['priceDimensions'])[0]
    price = float(od[id1]['priceDimensions'][id2]['pricePerUnit']['USD'])
    return price * 732

def handle_limit_exceeded_exception(error, filename):
        logging.basicConfig(level=logging.WARNING)
        logger = logging.getLogger()
        if error.response['Error']['Code'] == 'LimitExceededException':
                logger.warning('API call limit exceeded; backing off and retrying...')
        else:
                logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in {}'.format(sys.exc_info()[-1].tb_lineno), filename)
        