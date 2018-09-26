import fileinput
import sys
import openpyxl
import os
import stat
import shutil
import distutils.dir_util
import argparse
import subprocess

class CIQ_parser:
    def __init__(self, m_ciq="", m_az=""):
        self.ciq_fn = m_ciq
        self.az_fn = m_az
        self.nodesConf = dict()

    def __repr__(self):
        return '(%s)' % (self.ciq_fn)

    def parse_az_txt(self):
        param_file = self.az_fn
        print("FETCHING Availability zone env file")
        node_name = "unknown"
        if not os.path.isfile(param_file):
            print("There is no Availability zone env file")
            exit()
        with open(param_file, 'r') as f:
            for line in f:
                if line.startswith(">"):
                    node_name = line.strip().strip(">")
                elif "=" in line:
                    params = line.strip().split('=')
                    self.nodesConf[node_name][params[0].strip()] = params[1].strip()

    def parse_excel(self):
        #    param_file = os.getcwd() + "/templates_orig/Parameters.xlsx"
        #    param_file = os.getcwd() + "/templates_orig/CIQ.xlsx"
        param_file = self.ciq_fn
        print("FETCHING SITE SPECIFIC CUSTOMIZED PARAM")
        try:
            excel_document = openpyxl.load_workbook(param_file)
        except IOError as e:
            print(e.strerror)
            print("It is not a valid CIQ file")
            exit()
        nodes_list = excel_document.get_sheet_names()
        for name in nodes_list:
            m_sheet = excel_document.get_sheet_by_name(name)
            self.nodesConf[name] = dict()
            for i in range(6, len(m_sheet["A"])):
                if (m_sheet["B"][i].value is None) or (m_sheet["A"][i].value is None):
                    continue
                if "CIDR" in m_sheet["A"][i].value:
                    try:
                        class_str = m_sheet["A"][i].value.split("_CIDR")[0]
                        m1 = __import__("node_cidr")
                        my_class = getattr(m1, class_str)
                        my_instance = my_class(m_sheet["B"][i].value, name)
                        my_instance.fill_nodes_conf(self.nodesConf)
                    except (ImportError,AttributeError) as e:
                        print("continue to handle parameter")
                B = m_sheet["B"][i].value
                if type(B) is not str:
                    B = str(B)
                self.nodesConf[name][m_sheet["A"][i].value.strip()] = B.strip()
            #print(self.nodesConf[name])

    def get_nodesConf(self):
        return self.nodesConf
