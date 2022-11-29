import csv
import logging
import os
import sys
from datetime import datetime
import boto3


class GENINV:
    """Generates XLSX Sheet"""
    def __init__(self, inventory_info=None, dir_path=None, current_datetime=None):
        self.inventory_info = inventory_info
        self.dir_path = dir_path
        self.current_datetime = current_datetime
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()
        

    def generate_inv(self):
        try:
            #Generating inventory
            with open(f"{self.dir_path}/pennypincher_inventory.csv", "w", newline="") as inv:
                summary_writer = csv.writer(inv)
                summary_writer.writerows([self.inventory_info[list(self.inventory_info.keys())[0]]['Resources'][0]])
                for resource_type in self.inventory_info.keys():
                    summary_writer.writerows(self.inventory_info[resource_type]['Resources'][1:])                        

        except Exception as e:
            self.logger.error(
                "Error on line {} in generate_csv.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)

  