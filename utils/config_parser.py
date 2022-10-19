# from distutils.command.config import config
# import sys
# from configparser import ConfigParser
# import json
# import logging

# class CONFIGPARSER:
#     """To read/update the cloudwatch configuration from config.cfg file."""
  
#     def __init__(self, config='null'):
#         self.config = config
#         self.config_file_path = './utils/config.cfg'
#         logging.basicConfig(level=logging.WARNING)
#         self.logger = logging.getLogger()

#     def get_config(self):    
#         """Config can be either null or given in format ebs=15, lb=20, rds=30."""
#         try:
#             parser = ConfigParser()
#             parser.read(self.config_file_path)
#             if self.config.lower() != 'null':
#                 cfgs = self.config.split(',')
#                 for cfg in cfgs:
#                     resource = cfg.split('=')[0].strip().upper()
#                     cloudwatch_metrics_days = int(cfg.split('=')[1].strip())
#                     cloudwatch_metrics_period = cloudwatch_metrics_days * 86400
#                     parser.set(resource, 'cloudwatch_metrics_days', str(cloudwatch_metrics_days))
#                     parser.set(resource, 'cloudwatch_metrics_period', str(cloudwatch_metrics_period))
#                 config_dict = json.loads(json.dumps(parser._sections))
#                 print(config_dict)
#                 return config_dict
#             else:
#                 config_dict = json.loads(json.dumps(parser._sections))
#                 print(config_dict)
#                 return config_dict

#         except Exception as e:
#             self.logger.error(
#                 "Error on line {} in config_parser.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
#                 str(e))
#             sys.exit(1)

import os
import re
import yaml

def merges(default, overwrite):
  config=default.copy()
  for element in config:
    overwrite_keys=list(overwrite[element].keys())
    for resource_name in overwrite_keys:
      config[element][resource_name]=overwrite[element][resource_name]
  return(config)

def parse_config(path=None, data=None, tag='!ENV'):
    """
    Load a yaml configuration file and resolve any environment variables
    The environment variables must have !ENV before them and be in this format
    to be parsed: ${VAR_NAME}.
    E.g.:
    database:
        host: !ENV ${HOST}
        port: !ENV ${PORT}
    app:
        log_path: !ENV '/var/${LOG_PATH}'
        something_else: !ENV '${AWESOME_ENV_VAR}/var/${A_SECOND_AWESOME_VAR}'
    :param str path: the path to the yaml file
    :param str data: the yaml data itself as a stream
    :param str tag: the tag to look for
    :return: the dict configuration
    :rtype: dict[str, T]
    """
    # pattern for global vars: look for ${word}
    pattern = re.compile('.*?\${(\w+)}.*?')
    loader = yaml.SafeLoader

    # the tag will be used to mark where to start searching for the pattern
    # e.g. somekey: !ENV somestring${MYENVVAR}blah blah blah
    loader.add_implicit_resolver(tag, pattern, None)

    def constructor_env_variables(loader, node):
        value = loader.construct_scalar(node)
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                full_value = full_value.replace(
                    f'${{{g}}}', os.environ.get(g, g)
                )
            return full_value
        return value

    loader.add_constructor(tag, constructor_env_variables)

    if path:
        with open(path) as conf_data:
            return yaml.load(conf_data, Loader=loader)
    elif data:
        return yaml.load(data, Loader=loader)
    else:
        raise ValueError('Either a path or data should be defined as input')

conf = parse_config(path='config.yaml')
print(conf)