import sys
from configparser import ConfigParser
import json
import logging

class CONFIGPARSER:
    """To read/update the cloudwatch configuration from config.cfg file."""
  
    def __init__(self, config='null'):
        self.config = config
        self.config_file_path = './utils/config.cfg'
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def get_config(self):    
        """Config can be either null or given in format ebs=15, lb=20, rds=30."""
        try:
            parser = ConfigParser()
            parser.read(self.config_file_path)
            if self.config.lower() != 'null':
                cfgs = self.config.split(',')
                for cfg in cfgs:
                    resource = cfg.split('=')[0].strip().upper()
                    cloudwatch_metrics_days = int(cfg.split('=')[1].strip())
                    cloudwatch_metrics_period = cloudwatch_metrics_days * 86400
                    parser.set(resource, 'cloudwatch_metrics_days', str(cloudwatch_metrics_days))
                    parser.set(resource, 'cloudwatch_metrics_period', str(cloudwatch_metrics_period))
                config_dict = json.loads(json.dumps(parser._sections))
                return config_dict
            else:
                config_dict = json.loads(json.dumps(parser._sections))
                return config_dict

        except Exception as e:
            self.logger.error(
                "Error on line {} in config_parser.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)
