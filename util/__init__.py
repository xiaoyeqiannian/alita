import re
import xlsxwriter
from io import BytesIO
from flask import make_response

def make_excel_online(name, title, data):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    p = re.compile(r'[/\?:：\*\[\]]')
    name = re.sub(p,"",name)
    worksheet = workbook.add_worksheet(name)
    worksheet.write_row('A1', title)
    for i in range(len(data)):
        worksheet.write_row('A' + str(i + 2), data[i])
    workbook.close()
    response = make_response(output.getvalue())
    output.close()
    return response
