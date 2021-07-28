from tabulate import tabulate
from slack.errors import SlackApiError
import sys
import logging
import slack


class Slackalert:
    """To send cost report on slack."""
    def __init__(self, channel=None, slack_token=None):
        self.channel = channel
        self.slack_token = slack_token
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def get_resource_list(self, resource_name, resource_info, resource_header, resource_list, resource_savings):
        """Returns all the idle resource information in a dictionary format."""
        resource_list.insert(0, resource_header)
        resource_info[resource_name] = {}
        resource_info[resource_name]['Resources'] = resource_list
        resource_info[resource_name]['Savings'] = resource_savings
        return resource_info

    def slack_alert(self, resource_info, account_name, total_savings):
        """Creates a txt file which contains the cost report  and sends to the slack channel."""
        try:
            client = slack.WebClient(token=self.slack_token)

            f = open("/tmp/cost_optimization_report.txt", "w+")

            for res in resource_info.keys():       
                #Converts resource info dictionary to tabular format.
                f.write('\n' + 'Resource: ' + res + '\n')
                resource_table = tabulate(resource_info[res]['Resources'][1:],
                                          headers=resource_info[res]['Resources'][0], tablefmt="grid",
                                          disable_numparse=True)
                f.write('\n' + resource_table + '\n \n' + 'Savings: $' + str(resource_info[res]['Savings']) + '\n')
            f.close()
            response = client.files_upload(
                file='/tmp/cost_optimization_report.txt',
                initial_comment='Cost Optimization Report | ' + account_name + ' | Total Savings: $' + str(total_savings),
                channels=self.channel
            )

        except SlackApiError as e:
            """You will get a SlackApiError if "ok" is False."""
            assert e.response["ok"] is False
            assert e.response["error"]  
            """str like 'invalid_auth', 'channel_not_found'."""
            self.logger.error("Slack api error: {e.response['error']} | Error in slack_send.py")
            sys.exit(1)

        except Exception as e:
            self.logger.error(
                "Error on line {} in slack_send.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)
