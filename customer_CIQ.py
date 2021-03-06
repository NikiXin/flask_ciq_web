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
import predictionio
from datetime import datetime
import pytz
import random
import string

if __name__ == '__main__':

    user_list = list()
    for i in range(1,10):
        user=''.join(random.choice(string.ascii_lowercase) for n in range(5))
        user_list.append(user)
    print(user_list)
#    customer_conf = CIQ_parser("CIQ_Consolidated.xlsx")
#    customer_conf.parse_excel()
#    print(customer_conf.nodesConf)
#    m_ciq = CiqData("customer1", "project1", customer_conf.nodesConf)
#    m_ciq.dump_to_excel()
#    mtas = {"oam_vip": "10.0.0.10", "traffic_vip": "10.0.0.11"}
#    sbg = {"mip": "10.0.0.12", "access_ip": "10.0.0.13"}
#    project = {"mtas":mtas,"sbg":sbg}

#    m_redis = CiqRedis()
#    test_tools={"sap":"sap.jpg","calstore":"calstore.jpg"}
#    test_user1 = {"name":"test1","role":"sa","age":30}
#    test_user2 = {"name": "test2", "role": "si", "age": 25}
#    m_redis.set_user("user1", test_user1)
#    m_redis.set_user("user2", test_user2)
#    m_redis.read_users()
#    print(m_redis.get_user_list())
    #print(m_redis.get_user("user2"))
#    m_redis.set_tools(test_tools)
#    m_redis.write_tools()
#    m_redis.get_tools()
#    print(m_redis.get_tools())
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
    # Create a FileExporter and specify "my_events.json" as destination file
#    exporter = predictionio.FileExporter(file_name="my_events.json")
#
#    event_properties = {
#        "categories" : "tool",
#    }
#    # write the events to a file
#    event_response = exporter.create_event(
#        event="set",
#        entity_type="item",
#        entity_id="ESS",
#        properties=event_properties,
#        event_time=datetime(2014, 12, 13, 21, 38, 45, 618000, pytz.utc))
#    exporter.close()
