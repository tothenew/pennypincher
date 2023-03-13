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
                        html,
        body {
          height: 100%;
          text-align: left;
        }

        body {
          margin: 10;
          background: linear-gradient(to right, #F5F7FA,#B8C6DB);
          font-family: sans-serif;
          font-weight: 100;
        }


        table {
          width: 80%;
          height: 40%;
          border-collapse: collapse;
          overflow: hidden;
          box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }

        th,
        td {
          padding: 15px;
          background-color: rgba(255,255,255,0.2);
          color: #000;
        }

        th {
          text-align: left;
        }

        th {
          background-color: #bec5e2;
        }

        tr:hover {
          background-color: rgba(255,255,255,0.3);
        }
        
        td {
          position: relative;
        }

        td:hover:before {
          content: "";
          left: 0;
          right: 0;
          background-color: rgba(255,255,255,0.2);
        }

        /* h2,h3,h4{
          text-align: center;
        } */

        /* img{
          display: block;
          margin-left: auto;
          margin-right: auto;
        } */
                        </style>
                    </head>
                    <body>"""
        return html_prefix

    def get_HTML_infix(self):   
        """To display resource name in page."""
        html_infix = "<h4> Resource - "
        return html_infix

    def get_HTML_suffix(self):
        html_suffix = "<br></body></html>"
        return html_suffix

    def header_to_html(self, header):
        html = "<table><tr>"
        for i in header:
            if i == "Criteria":
                continue
            else:
                html = html + "<th>%s</th>" % (i)
        html = html + "</tr>"
        return html

    def body_to_html(self, body, savings):   
        """Generates html table with list of lists."""
        html = ''
        for result in body:
            html = html + '<tr>'
            for i in result:
                if result.index(i) == 9:
                    continue
                else:
                    html = html + "<td>%s</td>" % (i)
            html = html + "</tr>"
        html = html + "</table>"
        html = html + "<br><b> Total Savings = $%s </b>" % (round(savings, 2))
        return html

    def get_html_page(self, resource_name, headers, ebs_list, savings): 
        """Generates html page."""
        # try:
        msg_list = []
        html = self.header_to_html(headers)  # Table Header
        ebs_table = self.body_to_html(ebs_list, savings)  # Table Values
        msg_list.append([ebs_table, resource_name])  # Append value to final result list
        html_infix = self.get_HTML_infix()
        criteria = "<h4>"+headers[9]+" : "+ebs_list[0][9]+"</h4>"
        for resource in msg_list:
            html = html_infix + resource[1] + " : </h4>" + criteria + html + resource[0]
        return html
        # except Exception as e:
        #     self.logger.error(
        #         "Error on line {} in html_functions.py".format(sys.exc_info()[-1].tb_lineno) + " | Message: " +
        #         str(e))
        #     sys.exit(1)

