import os
import re
import yaml

def merges(default, overwrite):
  config=default.copy()
  if overwrite != None:
    for element in config:
        if element in overwrite:
            overwrite_keys=list(overwrite[element].keys())
            for resource_name in overwrite_keys:
                config[element][resource_name]={**config[element][resource_name], **overwrite[element][resource_name]}
  return(config)

def check_env(config):
    env_list = ["CHANNEL_NAME","SLACK_TOKEN","CONFIG","FROM_ADDRESS","TO_ADDRESS","SES_REGION","REPORTING_PLATFORM","ACCOUNT_NAME","REPORT_BUCKET","WEBHOOK_URL"] 
    for key in env_list:
        if key.lower() in config:
            config[key.lower()] = os.getenv(key,config[key.lower()])
    return config

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
