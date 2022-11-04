import os
import logging
import sys
import csv
from datetime import datetime

class GENCSV:
    """Generates XLSX Sheet"""
    def __init__(self, resource_info=None, total_savings=None, dir_path=None, current_datetime=None):
        self.resource_info = resource_info
        self.total_savings = total_savings
        self.dir_path = dir_path
        self.current_datetime = current_datetime
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def generate_csv(self):
        try:
            #Generating summary report
            with open(f"{self.dir_path}/pennypincher_summary_report.csv", "w", newline="") as summary:
                summary_writer = csv.writer(summary)
                summary_writer.writerows([self.resource_info[list(self.resource_info.keys())[0]]['Resources'][0]])
                for resource_type in self.resource_info.keys():
                    summary_writer.writerows(self.resource_info[resource_type]['Resources'][1:])
            
            #Generating individual resource report
            for resource_type in self.resource_info.keys():
                with open(f"{self.dir_path}/pennypincher_{resource_type}_report.csv", "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(self.resource_info[resource_type]['Resources'])
        except Exception as e:
            self.logger.error(
                "Error on line {} in generate_csv.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)
