import datetime
import sys
import logging
from botocore import exceptions


class CLOUDWATCH_UTILS:
    '''Contains functions for fetching cloudwatch metrics for resources'''
    def __init__(self, client):
        self.client = client
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def ec2_get_avg_max_metric(self, namespace, metric_name, dimension_name, dimension_value, config):
        # Returns Average, Maximum of the metric specified for ec2
        try:
            now = datetime.datetime.utcnow()
            start_time = (now - datetime.timedelta(days=int(config['cloudwatch_metrics_days']))).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
            response = self.client.get_metric_statistics(
                Namespace=namespace, MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': dimension_name,
                        'Value': dimension_value
                    }
                ],
                StartTime=start_time, EndTime=end_time, Period=3600,
                Statistics=['Average', 'Maximum'],
                Unit='Percent'
            )
            datapoints_len = len(response['Datapoints'])
            response = self.client.get_metric_statistics(
                Namespace=namespace, MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': dimension_name,
                        'Value': dimension_value
                    }
                ],
                StartTime=start_time, EndTime=end_time, Period=int(config['cloudwatch_metrics_period']),
                Statistics=['Average', 'Maximum'],
                Unit='Percent'
            )
            avg = 0
            peak = 0
            for cpu in response['Datapoints']:
                if 'Average' in cpu:
                    avg = cpu['Average']
                if 'Maximum' in cpu:
                    if cpu['Maximum'] > peak:
                        peak = cpu['Maximum']
            if datapoints_len > 24:
                return avg, peak, 'Ok'
            else:
                return avg, peak, 'Adhoc'
        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in cloudwatch_utils.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)
        except Exception as e:
            self.logger.error(
                "Error on line {} in cloudwatch_utils.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: "
                + str(e))
            sys.exit(1)

    def get_sum_metric(self, namespace, metric_name, dimension_name, dimension_value, config):
        # Returns sum of the metric specified with 1 dimension as input
        try:
            now = datetime.datetime.utcnow()
            start_time = (now - datetime.timedelta(days=int(config['cloudwatch_metrics_days']))).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
            response = self.client.get_metric_statistics(
                Namespace=namespace, MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': dimension_name,
                        'Value': dimension_value
                    },
                ],
                StartTime=start_time, EndTime=end_time, Period=int(config['cloudwatch_metrics_period']),
                Statistics=['Sum']
            )
            if response['Datapoints']:
                Sum = response['Datapoints'][0]['Sum']
            else:
                Sum = 0
            return Sum

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in cloudwatch_utils.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)
        except Exception as e:
            self.logger.error(
                "Error on line {} in cloudwatch_utils.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: "
                + str(e))
            sys.exit(1)

    def get_sum_metric2(self, namespace, metric_name, dimension_name1, dimension_value1, dimension_name2,
                        dimension_value2, config):
        # Returns sum of the metric specified with 2 dimensions as input
        try:
            now = datetime.datetime.utcnow()
            start_time = (now - datetime.timedelta(days=int(config['cloudwatch_metrics_days']))).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
            response = self.client.get_metric_statistics(
                Namespace=namespace, MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': dimension_name1,
                        'Value': dimension_value1
                    },
                    {
                        'Name': dimension_name2,
                        'Value': dimension_value2
                    },
                ],
                StartTime=start_time, EndTime=end_time, Period=int(config['cloudwatch_metrics_period']),
                Statistics=['Sum']
            )
            if response['Datapoints']:
                Sum = response['Datapoints'][0]['Sum']
            else:
                Sum = 0
            return Sum

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in cloudwatch_utils.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)
        except Exception as e:
            self.logger.error(
                "Error on line {} in cloudwatch_utils.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: "
                + str(e))
            sys.exit(1)

    def get_avg_metric(self, namespace, metric_name, dimension_name, dimension_value, config):
        # Returns average of the metric specified with 1 dimension as input
        try:
            now = datetime.datetime.utcnow()
            start_time = (now - datetime.timedelta(days=int(config['cloudwatch_metrics_days']))).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
            response = self.client.get_metric_statistics(
                Namespace=namespace, MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': dimension_name,
                        'Value': dimension_value
                    },
                ],
                StartTime=start_time, EndTime=end_time, Period=int(config['cloudwatch_metrics_period']),
                Statistics=['Average'], Unit='Percent'
            )
            if response['Datapoints']:
                Avg = response['Datapoints'][0]['Average']
            else:
                Avg = 0
            return Avg

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in cloudwatch_utils.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in cloudwatch_utils.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: "
                + str(e))
            sys.exit(1)

    def get_avg_max_metric(self, namespace, metric_name, dimension_name, dimension_value, config):
        # Returns average and maximum of the metric specified with 1 dimension as input
        try:
            now = datetime.datetime.utcnow()
            start_time = (now - datetime.timedelta(days=int(config['cloudwatch_metrics_days']))).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
            response = self.client.get_metric_statistics(
                Namespace=namespace, MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': dimension_name,
                        'Value': dimension_value
                    }
                ],
                StartTime=start_time, EndTime=end_time, Period=int(config['cloudwatch_metrics_period']),
                Statistics=['Average', 'Maximum'],
                Unit='Percent'
            )
            avg = 0
            peak = 0
            for cpu in response['Datapoints']:
                if 'Average' in cpu:
                    avg = cpu['Average']
                if 'Maximum' in cpu:
                    if cpu['Maximum'] > peak:
                        peak = cpu['Maximum']
            return avg, peak
        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in cloudwatch_utils.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in cloudwatch_utils.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: "
                + str(e))
            sys.exit(1)

    def get_avg_metric2(self, namespace, metric_name, dimension_name1, dimension_value1, dimension_name2,
                        dimension_value2, config):
        # Returns average of the metric specified with 2 dimensions as input
        try:
            now = datetime.datetime.utcnow()
            start_time = (now - datetime.timedelta(days=int(config['cloudwatch_metrics_days']))).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
            response = self.client.get_metric_statistics(
                Namespace=namespace, MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': dimension_name1,
                        'Value': dimension_value1
                    },
                    {
                        'Name': dimension_name2,
                        'Value': dimension_value2
                    },
                ],
                StartTime=start_time, EndTime=end_time, Period=int(config['cloudwatch_metrics_period']),
                Statistics=['Average']
            )
            if response['Datapoints']:
                Avg = response['Datapoints'][0]['Average']
            else:
                Avg = 0
            return Avg

        except exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                self.logger.warning('API call limit exceeded; backing off and retrying...')
            else:
                self.logger.error(error.response['Error']['Code'] + ': ' + error.response['Error']['Message'] +
                                  ' | Line {} in cloudwatch_utils.py'.format(sys.exc_info()[-1].tb_lineno))
                sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in cloudwatch_utils.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: "
                + str(e))
            sys.exit(1)
