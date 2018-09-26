import json
import redis
import xlsxwriter
import time
import os
from CIQ_redis import *


class CiqData:

    def __init__(self, customer, project):
        self.m_customer = customer
        self.m_project = project

    def dump_to_excel(self, ciq):
        unix_time = int(time.time())
        m_ciq = ciq
        m_dir = os.path.dirname(__file__)
        m_filename = m_dir + "\\" +  (self.m_customer + '_' + self.m_project + '_' + str(unix_time) + '.xlsx')

        workbook = xlsxwriter.Workbook(m_filename)

        merge_format_1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'yellow'})

        merge_format_2 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'Blue-Grey'})

        for node in m_ciq:
            worksheet = workbook.add_worksheet(node)
            m_node = m_ciq[node]
            worksheet.set_column(0, 2, 25)
            worksheet.merge_range('A2:A3', "Parameter Name", merge_format_1)
            worksheet.merge_range('B2:B3', "Reference Value used", merge_format_1)
            worksheet.merge_range('C2:C3', "Description", merge_format_1)
            worksheet.merge_range('A4:A5', "test", merge_format_2)
            worksheet.merge_range('B4:B5', "test", merge_format_2)
            worksheet.merge_range('C4:C5', "test", merge_format_2)
            worksheet.write(5,0,"name")
            worksheet.write(5,1,"value")
            row = 5
            col = 0
            for param in m_node:
                row += 1
                worksheet.write(row, col, param)
                worksheet.write(row, col+1, m_node[param])
        workbook.close()

    def fetch_ciq_from_redis(self):
        my_redis = CiqRedis()
        m_nodes = my_redis.get_set(self.m_customer + self.m_project)
        m_dict = dict()
        for node in m_nodes:
            m_attrs = my_redis.get_hash(self.m_customer + self.m_project + node)
            m_dict[node] = m_attrs
        return m_dict