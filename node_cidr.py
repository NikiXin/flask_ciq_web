import netaddr
import sys


class GeneralNet(object):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, **kwargs ):
        self.param_init(kwargs.get("m_nodeName"),kwargs.get("m_netName"), kwargs.get("m_subnet"), kwargs.get("m_dhcp"), kwargs.get("m_isBrf"))
        if kwargs.get("m_isManagement"):
            self.param_manager_net(kwargs.get("m_isManagement"), kwargs.get("m_hasMip"))
        if kwargs.get("m_isEvip"):
            self.param_evip_net(kwargs.get("m_isEvip"), kwargs.get("m_numberOfFee"))
        else:
            self.param_normal_net(kwargs.get("m_numberOfIp"))
        self.decode_subnet()

    def param_init(self, m_nodeName = "general", m_netName = "general", m_subnet = "0.0.0.0/0", m_dhcp = False, m_isBrf = True):
        ##General information
        self.node_subnet = m_subnet
        self.nodeName = m_nodeName
        self.netName = m_netName
        self.dhcp_enable = m_dhcp
        self.isBrf = m_isBrf
        ##For Management Net: SC-1, SC-2, Mip(optional)
        self.SC1_IP = None
        self.SC2_IP = None
        self.MIP_IP = None
        self.hasMip = None
        self.isManagement = None
        ##For evip network
        self.fee_IP = list()
        self.isEvip = None
        self.numberOfFee = None
        ##For CMX configuration
        self.CMX_L = None
        self.CMX_R = None
        self.CMX_VRRP = None
        ##For normal network
        self.net_IP = list()
        self.start_IP = None
        self.end_IP = None
        self.numberOfIp = None

    def param_manager_net(self, m_isManagement = True, m_hasMip = True):
        self.hasMip = m_hasMip
        self.isManagement = m_isManagement

    def param_evip_net(self, m_isEvip = True, m_numberOfFee = 2):
        self.isEvip = m_isEvip
        self.numberOfFee = m_numberOfFee

    def param_normal_net(self, m_numberOfIp):
        self.numberOfIp = m_numberOfIp

    def set_SC1_IP(self, m_ip):
        self.SC1_IP = m_ip

    def get_SC1_IP(self):
        return self.SC1_IP

    def set_SC2_IP(self, m_ip):
        self.SC2_IP = m_ip

    def get_SC2_IP(self):
        return self.SC2_IP

    def set_mip_IP(self, m_ip):
        self.MIP_IP = m_ip

    def get_mip_IP(self):
        return self.MIP_IP

    def set_start_IP(self, m_ip):
        self.start_IP = m_ip

    def get_start_IP(self):
        return self.start_IP

    def set_end_IP(self, m_ip):
        self.end_IP = m_ip

    def get_end_IP(self):
        return self.end_IP

    def set_CMX_L(self, m_ip):
        self.CMX_L = m_ip

    def get_CMX_L(self):
        return self.CMX_L

    def set_CMX_R(self, m_ip):
        self.CMX_R = m_ip

    def get_CMX_R(self):
        return self.CMX_R

    def set_CMX_vrrp(self, m_ip):
        self.CMX_VRRP = m_ip

    def get_CMX_vrrp(self):
        return self.CMX_VRRP

    def set_NET_IP(self, m_ip):
        self.net_IP.append(m_ip)

    def get_NET_IP(self):
        return self.net_IP

    def set_fee_IP(self, m_ip):
        self.fee_IP.append(m_ip)

    def get_fee_IP(self):
        return self.fee_IP

    def decode_subnet(self):
        try:
            ipn = netaddr.IPNetwork(self.node_subnet)
        except Exception as e:
            print(str(self.node_subnet) + " is not a valid subnet")
            print(e)
            exit(1)
        ip_list = list(ipn[1:len(ipn)-1])

        if self.isBrf:
            self.set_CMX_L(str(ip_list.pop(0)) + "/" + str(ipn.prefixlen))
            self.set_CMX_R(str(ip_list.pop(0)) + "/" + str(ipn.prefixlen))
        else:
            self.set_CMX_vrrp(ip_list.pop(0))
            self.set_CMX_L(str(ip_list.pop(0)) + "/" + str(ipn.prefixlen))
            self.set_CMX_R(str(ip_list.pop(0)) + "/" + str(ipn.prefixlen))

        if self.isEvip:
            for i in range(self.numberOfFee):
                self.set_fee_IP(ip_list.pop(0))

        elif self.isManagement:
            if not self.dhcp_enable:
                self.set_SC1_IP(ip_list.pop(0))
                self.set_SC2_IP(ip_list.pop(0))
                if self.hasMip:
                    self.set_mip_IP(ip_list.pop(0))
            else:
                self.set_mip_IP(ip_list.pop(0))
                self.set_start_IP(ip_list.pop(0))
                self.set_end_IP(ip_list[len(ip_list)-1])

        else:
            if self.dhcp_enable:
                self.set_start_IP(ip_list.pop(0))
                self.set_end_IP(ip_list[len(ip_list)-1])
            else:
                for i in range(self.numberOfIp):
                    self.set_NET_IP(ip_list.pop(0))

    def fill_nodes_conf(self, m_nodes_conf):
        self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_LEFT", str(self.get_CMX_L()))
        self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_RIGHT", str(self.get_CMX_R()))
        self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_GATEWAY_IPV4_ADDR",
                        str(self.get_CMX_vrrp()))
        if self.get_SC1_IP() is not None:
            self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_SC-1_IPV4_ADDR", str(self.get_SC1_IP()))
        if self.get_SC2_IP() is not None:
            self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_SC-2_IPV4_ADDR", str(self.get_SC2_IP()))
        if self.get_mip_IP() is not None:
            self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_OM_IPV4_ADDR", str(self.get_mip_IP()))
        if self.get_start_IP() is not None:
            self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_START_IPV4_ADDR", str(self.get_start_IP()))
        if self.get_end_IP() is not None:
            self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_END_IPV4_ADDR", str(self.get_end_IP()))
        if len(self.get_NET_IP()) > 0:
            ip_list = self.get_NET_IP()
            num_ip = 1
            for m_ip in ip_list:
                self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_IPV4_ADDR" + str(num_ip), str(m_ip))
                num_ip = num_ip + 1
        if len(self.get_fee_IP()) > 0:
            fee_list = self.get_fee_IP()
            num_fee = 1
            for fee_ip in fee_list:
                self.store_dict(m_nodes_conf, self.nodeName, self.nodeName + "_" + self.netName + "_FEE_LOCAL_" + str(num_fee), str(fee_ip))
                num_fee = num_fee + 1

    def store_dict(self, m_nodes_conf, key1, key2, value):
        try:
            m_nodes_conf[key1][key2] = value
        except KeyError:
            m_nodes_conf[key1] = dict()
            m_nodes_conf[key1][key2] = value

'''(self, m_subnet="0.0.0.0/0", m_nodeName="general", m_netName = "general", m_dhcp = False, m_mip = False, m_evip = False, m_brf = False, m_numOfFee = 2 )'''

class MTAS_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0",  nodeName="MTAS",  netName = "MANAGEMENT",  dhcp = False, isBrf = False, hasMip = True, isManagement = True ):
        super(MTAS_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                  m_isBrf = isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class CSCF_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="CSCF", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(CSCF_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                  m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class SBG_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="SBG", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(SBG_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                 m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class SBG_CORE_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="SBG", netName = "CORE", dhcp = False, isBrf = False, numberOfIp = 1):
        super(SBG_CORE_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                           m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class SBG_ACCESS_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="SBG", netName = "ACCESS", dhcp = False, isBrf = False, numberOfIp = 1):
        super(SBG_ACCESS_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                             m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class SBG_LI_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="SBG", netName = "LI", dhcp = False, isBrf = False, numberOfIp = 1):
        super(SBG_LI_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                         m_isBrf=isBrf, m_numberOfIp= numberOfIp)
class IBCF_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IBCF", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(IBCF_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                 m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class IBCF_CORE_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IBCF", netName = "CORE", dhcp = False, isBrf = False, numberOfIp = 1):
        super(IBCF_CORE_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                           m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class IBCF_FOREIGN_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IBCF", netName = "FOREIGN", dhcp = False, isBrf = False, numberOfIp = 1):
        super(IBCF_FOREIGN_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                             m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class IBCF_LI_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IBCF", netName = "LI", dhcp = False, isBrf = False, numberOfIp = 1):
        super(IBCF_LI_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                         m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class HSS_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="HSS", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = False, isManagement = True):
        super(HSS_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                 m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class CUDB_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="CUDB", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = False, isManagement = True):
        super(CUDB_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                  m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class BGF_SIGNALING_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="BGF", netName = "SIGNALING", dhcp = True, isBrf = False, numberOfIp = 1):
        super(BGF_SIGNALING_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class BGF_UNTRUSTED1_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="BGF", netName = "UNTRUSTED1", dhcp = True, isBrf = False, numberOfIp = 1):
        super(BGF_UNTRUSTED1_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class BGF_UNTRUSTED2_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="BGF", netName = "UNTRUSTED2", dhcp = True, isBrf = False, numberOfIp = 1):
        super(BGF_UNTRUSTED2_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                 m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class BGF_TRUSTED_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="BGF", netName = "TRUSTED", dhcp = True, isBrf = False, numberOfIp = 1):
        super(BGF_TRUSTED_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                              m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class BGF_LI_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="BGF", netName = "LI", dhcp = True, isBrf = False, numberOfIp = 1):
        super(BGF_LI_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                         m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class BGF_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="BGF", netName = "MANAGEMENT", dhcp = True, isBrf = False, hasMip = True, isManagement = True):
        super(BGF_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                 m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class MRF_SIGNALING_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="MRF", netName = "SIGNALING", dhcp = True, isBrf = False, numberOfIp = 1):
        super(MRF_SIGNALING_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class MRF_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="MRF", netName = "MANAGEMENT", dhcp = True, isBrf = False, hasMip = True, isManagement = True):
        super(MRF_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                 m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class MRF_MEDIA_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="MRF", netName = "MEDIA", dhcp = True, isBrf = False, numberOfIp = 1):
        super(MRF_MEDIA_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                            m_isBrf=isBrf, m_numberOfIp= numberOfIp)

class IPWDNS_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IPWDNS", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(IPWDNS_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                    m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class IPWDNS_PROV_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IPWDNS", netName = "PROV", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(IPWDNS_PROV_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                              m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class IPWAAA_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IPWAAA", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(IPWAAA_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                    m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class IPWAAA_PROV_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IPWAAA", netName = "PROV", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(IPWAAA_PROV_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                              m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class EME_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="EME", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(EME_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                 m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class NELS_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="NELS", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(NELS_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                  m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class DSC_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="DSC", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(DSC_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                 m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class IPWeDNS_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IPWeDNS", netName = "MANAGEMENT", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(IPWeDNS_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                                     m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class IPWeDNS_PROV_NET(GeneralNet):
    ''' Class used for CIDR (SC1-ip, SC2-ip, mip)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="IPWeDNS", netName = "PROV", dhcp = False, isBrf = False, hasMip = True, isManagement = True):
        super(IPWeDNS_PROV_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                               m_isBrf=isBrf, m_hasMip = hasMip, m_isManagement= isManagement)

class EDA_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (3 ip, CMX-L, CMX-R, CMX-VRRP)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="EDA", netName = "MANAGEMENT", dhcp = False, isBrf = False, numberOfIp = 3):
        super(EDA_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                               m_isBrf=isBrf, m_numberOfIp = numberOfIp)

class AFG_MANAGEMENT_NET(GeneralNet):
    ''' Class used for CIDR (5 ip, CMX-L, CMX-R, CMX-VRRP)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="AFG", netName = "MANAGEMENT", dhcp = False, isBrf = False, numberOfIp = 5):
        super(AFG_MANAGEMENT_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                               m_isBrf=isBrf, m_numberOfIp = numberOfIp)

class AFG_CTRL_NET(GeneralNet):
    ''' Class used for CIDR (1 ip, CMX-L, CMX-R, CMX-VRRP)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="AFG", netName = "CTRL", dhcp = False, isBrf = False, numberOfIp = 1):
        super(AFG_CTRL_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                               m_isBrf=isBrf, m_numberOfIp = numberOfIp)

class AFG_ACCESS_NET(GeneralNet):
    ''' Class used for CIDR (1 ip, CMX-L, CMX-R, CMX-VRRP)'''
    def __init__(self, subnet="0.0.0.0/0", nodeName="AFG", netName = "ACCESS", dhcp = False, isBrf = False, numberOfIp = 1):
        super(AFG_ACCESS_NET, self).__init__(m_subnet = subnet, m_nodeName = nodeName, m_netName = netName, m_dhcp = dhcp,
                                               m_isBrf=isBrf, m_numberOfIp = numberOfIp)
