import json
import redis


class CiqRedis:

    def __init__(self, m_host="127.0.0.1", m_port="6379"):
        self.r_conn = redis.StrictRedis(host=m_host, charset="utf-8", port=m_port, db=0, decode_responses=True)
        self.m_tools = dict()
        self.m_users = dict()
        self.m_users_list = list()

    def write_data(self, m_dict, m_key="ciq"):
        json_data = json.dumps(m_dict)
        self.r_conn.set(m_key, json_data)

    def get_data(self, m_key="ciq"):
        r_dict = dict()
        r_dict = json.loads(self.r_conn.get(m_key))
        return r_dict

    def get_all(self):
        r_list = list()
        r_list = self.r_conn.keys()
        return r_list
    
    def get_set(self, m_key="ciq"):
        r_set = self.r_conn.smembers(m_key)
        return r_set

    def set_set(self, m_value="", m_key="ciq"):
        self.r_conn.sadd(m_key, m_value)

    def is_member_set(self, m_value="",m_key="ciq"):
        r_member = self.r_conn.sismember(m_key,m_value)
        return r_member

    def get_hash(self, m_key="ciq"):
        r_hash=self.r_conn.hgetall(m_key)
        return r_hash

    def set_hash(self, m_name="", m_value="",m_key="ciq"):
        self.r_conn.hset(m_key, m_name, m_value)

    def set_m_hash(self, m_mapping, m_key="ciq"):
        self.r_conn.hmset(m_key,m_mapping)

#### for Hack4Easy! ######
    
    def set_tools(self, tools=dict()):
        self.m_tools = tools

    def get_tools(self):
        return self.m_tools

    def write_tools(self):
        for tool, icon in self.m_tools.items():
            self.r_conn.hset("tools", tool, icon)

    def read_tools(self):
        m_tools = self.r_conn.hgetall("tools")

    def write_users(self):
        for user_id in self.m_users.keys():
            self.r_conn.sadd("users", user_id)
        for user_id, user_profile in self.m_users.items():
            json_data = json.dumps(user_profile)
            self.r_conn.set(user_id, json_data)
    
    def read_users(self):
        self.m_users_list = self.r_conn.smembers("users")
        for userid in self.m_users_list:
            m_user = self.r_conn.get(userid)
            r_dict = json.loads(m_user)
            self.m_users[userid] = r_dict 

    def set_user(self, user_id, profile=dict()):
        self.m_users[user_id] = profile

    def get_user(self, user_id):
        return self.m_users[user_id]

    def get_user_list(self):
        return self.m_users_list
