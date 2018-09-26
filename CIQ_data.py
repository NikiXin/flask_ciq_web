import json
import redis
import xlsxwriter
import time
import os


class CiqData:

    def __init__(self, customer, project, ciq):
        self.m_ciq = ciq
        self.m_customer = customer
        self.m_project = project

    def dump_to_excel(self):
        unix_time = int(time.time())
        m_filename = os.path.abspath(os.path.dirname(__file__)) + (self.m_customer + '_' + self.m_project + '_' + str(unix_time) + '.xlsx')
        print(m_filename)
        workbook = xlsxwriter.Workbook(m_filename)

        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'yellow'})

        for node in self.m_ciq:
            worksheet = workbook.add_worksheet(node)
            m_node = self.m_ciq[node]
            worksheet.merge_range('A1:A2', "Parameter Name", merge_format)
            worksheet.merge_range('B1:B2', "Reference Value used", merge_format)
            worksheet.merge_range('C1:C2', "Description", merge_format)
            row = 1
            col = 0
            for param in m_node:
                row += 1
                worksheet.write(row, col, param)
                worksheet.write(row, col+1, m_node[param])
        workbook.close()

if __name__ == '__main__':
    mtas={"ip":"127.0.0.1", "user":"root"}
    sbg={"ip":"127.0.0.2", "user":"maintenance"}
    ciq = {"MTAS":mtas, "SBG":sbg}
    test = CiqData("test","proj1",ciq)
    test.dump_to_excel()