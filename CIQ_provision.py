import fileinput
import sys
import os
import stat
import shutil
import distutils.dir_util
import argparse
import subprocess

import netaddr


class ciqFunction(object):
    def __init__(self, m_text):
        #print("in ciqClass")
	#print("m_text")
        self.para_value = m_text

    def ciqsplit(self, m_delimeter, m_index):
        return self.para_value.split(m_delimeter.strip('\''))[int(m_index)]

#    def indexIpwithNet(self, m_delimeter, m_index):
#	    ipn = netaddr.IPNetwork(self.para_value)
#        return str(ipn[m_index]) + "/" + str(ipn.prefixlen)

class CIQ_provision(object):
    def __init__(self, m_nodesConf=dict(), m_directory="/"):
        #print("in CIQ provision")
        self.nodes_conf = m_nodesConf
        self.directory = m_directory

    def needCallFunction(self, m_parameter):
        m_parameter_list = list()
        m_parameter_list = m_parameter.split("->")
        return m_parameter_list

    def handlecallFunction(self, m_callFunction, m_value):
        m_function = m_callFunction.split('(')[0]
        m_args = m_callFunction.split('(')[1].split(')')[0].split(',')
        m_ciqFunction = ciqFunction(m_value)
        m_method = getattr(m_ciqFunction, m_function)
        return (m_method(m_args[0], m_args[1]))

    def crosseCheck(self, text):
        index = 0
        m_beg = m_end = m_pos = 0
        m_flag = 0
        m_delimeter = "{{"
        while index < len(text):
            if not m_flag:
                m_pos = text.find(m_delimeter, 0)
            else:
                m_pos = text.find(m_delimeter, index)
            if m_pos >= 0:
                if m_flag == 0:
                    m_flag = 1
                    m_beg = m_pos
                    m_delimeter = "}}"
                else:
                    m_end = m_pos + 2
                    m_flag = 0
                    m_parameter = text[m_beg:m_end]
                    m_parameter_strip = m_parameter.strip("{{").strip("}}")
                    m_delimeter_pos = m_parameter_strip.find('_')
                    m_node = m_parameter_strip[0:m_delimeter_pos]
                    try:
		        #print(m_parameter_strip)
                        m_parameter_list = self.needCallFunction(m_parameter_strip)
		        #print(m_parameter_list)
                        if len(m_parameter_list) > 1:
                            m_parameter_strip = m_parameter_list[0]
                            m_value = self.nodes_conf[m_node][m_parameter_strip]
                            m_value = self.handlecallFunction(m_parameter_list[1], m_value)
                        else:
                            m_value = self.nodes_conf[m_node][m_parameter_strip]
                    except KeyError:
                        m_value = "ERROR"
                    text = text.replace(m_parameter, m_value)
                    m_delimeter = "{{"
                index = m_pos + 1
            else:
                break
        return text


class Template_Provision(CIQ_provision):
    def __init__(self, m_nodesConf, m_directory="/", m_fileList = list()):
        m_directory = os.path.dirname(os.getcwd())
        super(Template_Provision, self).__init__(m_nodesConf, m_directory)
        self.file_list = tuple(m_fileList)

    def update_node(self):
        print("UPDATE HOT/configuration")
        node_list = self.nodes_conf.keys();
        base_dir = self.directory + "/templates"
        orig_dir = self.directory + "/templates_orig"
        if not os.path.isdir(orig_dir):
            exit(1)
        if os.path.isdir(base_dir):
            shutil.rmtree(base_dir)
        shutil.copytree(orig_dir, base_dir)
        for root, subdir, files in os.walk(base_dir):
            for m_dir in subdir:
                if m_dir in node_list:
                    node_dir = base_dir + "/" + m_dir + "/"
                    for root, subdir, files in os.walk(node_dir):
                        for m_file in files:
                            if m_file.endswith(self.file_list):
                                m_fullPath = os.path.join(root, m_file)
                                with open(m_fullPath, 'r') as f:
                                    text = f.read()
                                with open(m_fullPath, 'w') as f:
                                    f.write(self.crosseCheck(text))
                                    st = os.stat(m_fullPath)
                                    os.chmod(m_fullPath, st.st_mode | stat.S_IEXEC)


class Inventory_Provision(CIQ_provision):
    def __init__(self, m_nodesConf, m_directory="/", m_fileList = list()):
        m_directory = os.path.dirname(os.getcwd())
        super(Inventory_Provision, self).__init__(m_nodesConf, m_directory)
        self.file_list = tuple(m_fileList)
        #print("provision ansible inventory file")

    def update_inventory(self):
        print("UPDATE inventory file")
        f_inventory = self.directory + "/inventory"
        bk = f_inventory + "_bk"
        if not os.path.isfile(f_inventory):
            print("There is no inventory file for ansible")
            exit(1)
        if os.path.isfile(bk):
            print("The backup inventory file for ansible already exists, will create new backup inventory")
            try:
                os.remove(f_inventory)
                shutil.copyfile(bk, f_inventory)
            except OSError as exc:
                if exc.errno != 17:
                    raise
        else:
            try:
                shutil.copyfile(f_inventory, bk)
            except OSError as exc:
                if exc.errno != 17:
                    raise
        with open(f_inventory, 'r') as f:
            text = f.read()
        with open(f_inventory, 'w') as f:
            f.write(self.crosseCheck(text))


class Var_Provision(CIQ_provision):
    def __init__(self, m_nodesConf, m_directory="/", m_fileList = list()):
        m_directory = os.path.dirname(os.getcwd())
        super(Var_Provision, self).__init__(m_nodesConf, m_directory)
        self.file_list = tuple(m_fileList)
        #print("provision grobal var file")

    def update_vars(self):
        print("UPDATE global variable file")
        f_vars = self.directory + "/group_vars/all"
        bk = f_vars + "_bk"
        if not os.path.isfile(f_vars):
            print("There is no group vars for ansible")
            exit(1)
        if os.path.isfile(bk):
            print("group backup vars for ansible exists, will create new backup group var")
            try:
                os.remove(f_vars)
                shutil.copyfile(bk, f_vars)
            except OSError as exc:
                if exc.errno != 17:
                    raise
        else:
            try:
                shutil.copyfile(f_vars, bk)
            except OSError as exc:
                if exc.errno != 17:
                    raise
        with open(f_vars, 'r') as f:
            text = f.read()
        with open(f_vars, 'w') as f:
            f.write(self.crosseCheck(text))


class Cloud_Provision(CIQ_provision):
    def __init__(self, m_nodesConf, m_directory="/", m_fileList = list()):
        m_directory = os.path.dirname(os.getcwd())
        super(Cloud_Provision, self).__init__(m_nodesConf, m_directory)
        self.file_list = tuple(m_fileList)
        #print("provision CEE config.yaml")

    def update_cloud(self):
        print("UPDATE cee config.yaml")
        f_cee = self.directory + "/cloud_infra/config.yaml"
        bk = f_cee + "_bk"
        if not os.path.isfile(f_cee):
            print("There is no cee config.yaml")
            exit(1)
        if os.path.isfile(bk):
            print("The backup cee config.yaml already exists, will create new backup cee config.yaml")
            try:
                os.remove(f_cee)
                shutil.copyfile(bk, f_cee)
            except OSError as exc:
                if exc.errno != 17:
                    raise
        else:
            try:
                shutil.copyfile(f_cee, bk)
            except OSError as exc:
                if exc.errno != 17:
                    raise
        with open(f_cee, 'r') as f:
            text = f.read()
        with open(f_cee, 'w') as f:
            f.write(self.crosseCheck(text))


class SW_Provision(CIQ_provision):
    def __init__(self, m_nodesConf, m_directory="/", m_fileList = list()):
        m_directory = os.path.dirname(os.getcwd())
        super(SW_Provision, self).__init__(m_nodesConf, m_directory)
        self.file_list = tuple(m_fileList)
        #print("provision switch config")

    def update_sw(self):
        print("UPDATE switch configuration")
        f_sw = self.directory + "/cloud_infra/ECCA_Switch_Config.txt"
        bk = f_sw + "_bk"
        if not os.path.isfile(f_sw):
            print("There is no switch configuration")
            exit()
        if os.path.isfile(bk):
            print("The backup switch configuration already exists, will create new backup switch configuration")
            try:
                os.remove(f_sw)
                shutil.copyfile(bk, f_sw)
            except OSError as exc:
                if exc.errno != 17:
                    raise
        else:
            try:
                shutil.copyfile(f_sw, bk)
            except OSError as exc:
                if exc.errno != 17:
                    raise
        with open(f_sw, 'r') as f:
            text = f.read()
        with open(f_sw, 'w') as f:
            f.write(self.crosseCheck(text))
