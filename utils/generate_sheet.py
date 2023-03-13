import xlsxwriter
import os
import logging
import sys

class XLSX:
    """Generates XLSX Sheet"""
    def __init__(self, resource_info=None, total_savings=None, file_path=None):
        self.resource_info = resource_info
        self.total_savings = total_savings
        self.file_path = file_path
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def generate_xlsx_sheet(self):
        # try:
        row_number = 0

        workbook = xlsxwriter.Workbook(self.file_path)
        worksheet = workbook.add_worksheet()

        global_header_format = workbook.add_format({'bold': True, 'font_size': 20})
        resource_saving_format = workbook.add_format({'bold': True, 'font_size': 14})
        resource_header_format = workbook.add_format({'bold': True, 'font_size': 14, 'bg_color': '#C1C1C1','align':'center'})

        worksheet.write(row_number, 0, f"Cost Optimization Report | AWS Account | Total Savings: ${self.total_savings}", global_header_format)
        row_number+=2

        for resource_name in self.resource_info.keys():
            resource_saving = self.resource_info[resource_name]['Savings']
            worksheet.write(row_number, 0, f"Resource - {resource_name} :", resource_saving_format) #Writing Resource Name
            row_number = row_number + 1
            for col_num, data in enumerate(self.resource_info[resource_name]['Resources'][0]):
                worksheet.write(row_number, col_num, data, resource_header_format) #Writing Resource Header
            for resource_data in self.resource_info[resource_name]['Resources'][1:]:
                row_number = row_number + 1
                for col_num, data in enumerate(resource_data):
                    worksheet.write(row_number, col_num, data) #Writing Resource Data
            row_number = row_number + 1
            worksheet.write(row_number, 0, f"Total Savings = ${resource_saving}", resource_saving_format) #Writing Resource Total Saving
            row_number = row_number + 2
            
        workbook.close()
        # except Exception as e:
        #     self.logger.error(
        #         "Error on line {} in html_functions.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
        #         str(e))
        #     sys.exit(1)
