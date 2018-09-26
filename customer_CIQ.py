import fileinput
import sys
import os
import stat
import shutil
import distutils.dir_util
import argparse
import subprocess
import json
import redis
from CIQ_data import *
from CIQ_parser import *
from CIQ_redis import *

if __name__ == '__main__':

    customer_conf = CIQ_parser("CIQ_Consolidated.xlsx")
    customer_conf.parse_excel()
    print(customer_conf.nodesConf)
    m_ciq = CiqData("customer1", "project1", customer_conf.nodesConf)
    m_ciq.dump_to_excel()
#    mtas = {"oam_vip": "10.0.0.10", "traffic_vip": "10.0.0.11"}
#    sbg = {"mip": "10.0.0.12", "access_ip": "10.0.0.13"}
#    project = {"mtas":mtas,"sbg":sbg}

#    m_redis = CiqRedis()
#    m_redis.write_data(project, m_key="ATT_vIMS-1.6")
#    m_redis.write_data(project, m_key="ATT_ECC")
#    m_redis.write_data(project, m_key="SAMOA_ECC")
#    m_redis.set_set("ATT", "customer")
#    m_redis.set_set("SAMOA","customer")
#    m_redis.set_set("IMS-1.6","ATT")
#    m_redis.set_set("ECC", "ATT")
#    m_redis.set_set("ECC","SAMOA")
#    m_redis.set_set("mtas","ATTECC")
#    m_redis.set_set("sbg","ATTECC")
#    m_redis.set_set("cscf","SAMORECC")
#    m_redis.set_m_hash(mtas,"ATTECCmtas")
#    m_redis.set_m_hash(sbg,"ATTECCsbg")
