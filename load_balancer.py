"""
An OpenFlow Load Balancer implementation
"""
import logging
import random

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.packet import packet
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.lib.packet import icmp
from ryu.controller import dpset
from netaddr import *
from collections import namedtuple


class NAT(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
    global ip_map
    # map for internal IP and internal port
    ip_map = namedtuple("ip_map", ["addr", "port"])

    global EX_IP
    EX_IP = "128.128.129.1"

    global SLAVES
    SLAVES = ["192.168.1.11", "192.168.1.12", "192.168.1.13"]

    def __init__(self, *args, **kwargs):
        self.tcp_maps = {}
        self.udp_maps = {}

        self.tcp_ports = list(range(50000, 60000))
        self.udp_ports = list(range(50000, 60000))

        super(NAT, self).__init__(*args, **kwargs)

    def add_flow(self, datapath, match, actions, priority=0, hard_timeout=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match,
                                actions=actions, hard_timeout=hard_timeout, cookie=0, command=ofproto.OFPFC_ADD)
        datapath.send_msg(mod)
        # self.logger.info("add_flow:"+str(mod))

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def _event_switch_enter_handler(self, ev):
        dl_type_arp = 0x0806
        dl_type_ipv4 = 0x0800
        dl_type_ipv6 = 0x86dd
        dp = ev.dp
        ofproto = dp.ofproto
        parser = dp.ofproto_parser
        self.logger.info("switch connected %s", dp)

        # pass packet directly
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]

        # arp
        match = parser.OFPMatch(dl_type=dl_type_arp)

        self.add_flow(dp, match, actions)

        # ipv6
        match = parser.OFPMatch(dl_type=dl_type_ipv6)

        self.add_flow(dp, match, actions)

        # igmp
        match = parser.OFPMatch(dl_type=dl_type_ipv4, nw_proto=2)

        self.add_flow(dp, match, actions)

        # do address translation for following types of packet
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]

        # icmp
        match = parser.OFPMatch(dl_type=dl_type_ipv4, nw_proto=1)

        self.add_flow(dp, match, actions)

        # tcp
        match = parser.OFPMatch(dl_type=dl_type_ipv4, nw_proto=6)

        self.add_flow(dp, match, actions)

        # udp
        match = parser.OFPMatch(dl_type=dl_type_ipv4, nw_proto=17)

        self.add_flow(dp, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # self.logger.info("msg in")

        message = ev.msg
        # self.logger.info("message %s", message)
        datapath = message.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        pkt = packet.Packet(message.data)
        # self.logger.info("pkt %s", pkt)
        ip = pkt.get_protocol(ipv4.ipv4)
        # self.logger.info("ipv4 %s", ip)

        bitmask = "24"
        src_match = IPNetwork("192.168.1.0" + "/" + bitmask)
        dst_match = EX_IP

        tcpInfo = pkt.get_protocol(tcp.tcp)

        if IPNetwork(ip.src + "/" + bitmask) == src_match:
            # Destination is the outside from one of the slave nodes

            actions = [
                parser.OFPActionSetNwSrc(self.ipv4_to_int(EX_IP)),
                parser.OFPActionOutput(1)
            ]

            self.logger.info("Recieved packet from slave node " +
                             str(ip.src) + ", changing source to " + EX_IP)

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=message.buffer_id,
                                      data=message.data, in_port=message.in_port, actions=actions)

            datapath.send_msg(out)
        elif ip.dst == dst_match:
            # Destination is the load balancer (this)

            entry = ip_map(ip.src, tcpInfo.src_port)
            if entry in self.tcp_maps:
                slave_ip = self.tcp_maps[entry]
            else:
                slave_ip = random.choice(SLAVES)
                self.tcp_maps[entry] = slave_ip  # add entry for next time

            actions = [
                # Randomly choose one of the slave nodes
                parser.OFPActionSetNwDst(self.ipv4_to_int(slave_ip)),
                parser.OFPActionOutput(ofproto.OFPP_LOCAL)
            ]

            self.logger.info(
                "Recieved packet into the load balancer, sending to " + slave_ip)

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=message.buffer_id,
                                      data=message.data, in_port=message.in_port, actions=actions)

            datapath.send_msg(out)

    def ipv4_to_str(self, integre):
        ip_list = [str((integre >> (24 - (n * 8)) & 255)) for n in range(4)]
        return '.'.join(ip_list)

    def ipv4_to_int(self, string):
        ip = string.split('.')
        assert len(ip) == 4
        i = 0
        for b in ip:
            b = int(b)
            i = (i << 8) | b
        return i
