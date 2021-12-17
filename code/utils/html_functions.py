import logging
import sys


class HTML:
    """Generates html page to send as email."""
    def __init__(self, resource_name=None, headers=None, ebs_list=None, savings=None):
        self.headers = headers
        self.ebs_list = ebs_list
        self.savings = savings
        self.resource_name = resource_name
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def get_HTML_prefix(self):      
        """Returns html page header."""
        html_prefix = """ <html>
                    <head>
                        <style>
                        table, th, td {
                          border: 1px solid black;
                          border-collapse: collapse;
                          padding: 5px 15px;
                          text-align: center; 
                          vertical-align: middle;
                        }
                        </style>
                    </head>
                    <body>"""
        return html_prefix

    def get_HTML_infix(self):   
        """To display resource name in page."""
        html_infix = "<br><br><h4> Resource - "
        return html_infix

    def get_HTML_suffix(self):
        html_suffix = "<br></body></html>"
        return html_suffix

    def header_to_html(self, header):
        html = "<table><tr>"
        for i in header:
            html = html + "<th>%s</th>" % (i)
        html = html + "</tr>"
        return html

    def body_to_html(self, body, savings):   
        """Generates html table with list of lists."""
        html = ''
        for result in body:
            html = html + '<tr>'
            for i in result:
                html = html + "<td>%s</td>" % (i)
            html = html + "</tr>"
        html = html + "</table>"
        html = html + "<br><b> Total Savings = $%s </b>" % (round(savings, 2))
        return html

    def get_html_page(self, resource_name, headers, ebs_list, savings): 
        """Generates html page."""
        try:
            msg_list = []
            html = self.header_to_html(headers)  # Table Header
            ebs_table = self.body_to_html(ebs_list, savings)  # Table Values
            msg_list.append([ebs_table, resource_name])  # Append value to final result list
            html_infix = self.get_HTML_infix()
            for resource in msg_list:
                html = html_infix + resource[1] + " : </h4>" + html + resource[0]
            return html
        except Exception as e:
            self.logger.error(
                "Error on line {} in html_functions.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
                str(e))
            sys.exit(1)
