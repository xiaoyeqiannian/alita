import re
import time
import xlsxwriter
from io import BytesIO
from flask import make_response

def make_excel_online(name, title, data):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    # 去除sheet名字中的特殊字符，否则保存失败
    p = re.compile(r'[/\?:：\*\[\]]')
    name = re.sub(p,"",name)
    worksheet = workbook.add_worksheet(name)
    worksheet.write_row('A1', title)
    for i in range(len(data)):
        worksheet.write_row('A' + str(i + 2), data[i])
    workbook.close()
    response = make_response(output.getvalue())
    output.close()
    response.headers['Content-Type'] = "utf-8"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Disposition"] = "attachment; filename=%s.xlsx" % int(time.time())
    return response
