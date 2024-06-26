from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import ether_types
import requests
import logging

class DroneControl(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DroneControl, self).__init__(*args, **kwargs)
        self.logger.setLevel(logging.DEBUG)
        self.ovsdb_addr = 'tcp:127.0.0.1:6632'

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dpid = ev.msg.datapath.id
        self.logger.info("Switch connected: %s", hex(dpid))
        datapath = ev.msg.datapath
        self.setup_qos(datapath)
        self.install_flows(datapath)

    def setup_qos(self, datapath):
        dpid = datapath.id
        switch_id = format(dpid, "016x")
        queue_data = {
            "port_name": "s1-eth1",
            "type": "linux-htb",
            "max_rate": "1000000",
            "queues": [
                {"max_rate": "800000"},
                {"min_rate": "500000"}
            ]
        }

        # Set ovsdb_addr to access OVSDB
        url = f'http://localhost:8080/v1.0/conf/switches/{switch_id}/ovsdb_addr'
        requests.put(url, json=self.ovsdb_addr)

        # Apply Queue settings
        url = f'http://localhost:8080/qos/queue/{switch_id}'
        response = requests.post(url, json=queue_data)
        self.logger.info(f"Queue set: {response.json()}")

        # Set up meter table
        meter_data = {
            "meter_id": "1",
            "flags": "KBPS",
            "bands": [
                {"type": "DSCP_REMARK", "rate": "500"}
            ]
        }
        url = f'http://localhost:8080/qos/meter/{switch_id}'
        response = requests.post(url, json=meter_data)
        self.logger.info(f"Meter set: {response.json()}")

    def install_flows(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        # Define the port mappings based on the topology
        port_mapping = {
            0x0000000000000001: [1, 2, 3],
            0x0000000000000003: [1],
            0x0000000000100001: [2],
            0x0000000000100002: [2]
        }

        if dpid in port_mapping:
            for port in port_mapping[dpid]:
                match = parser.OFPMatch(
                    in_port=port,
                    dl_type=ether_types.ETH_TYPE_IP,
                    nw_proto=ipv4.inet.IPPROTO_TCP
                )
                actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
                self.add_flow(datapath, 200, match, actions)

                # Apply meter to the flow
                match = parser.OFPMatch(
                    in_port=port,
                    dl_type=ether_types.ETH_TYPE_IP,
                    nw_proto=ipv4.inet.IPPROTO_TCP
                )
                actions = [
                    parser.OFPActionMeter(meter_id=1),
                    parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)
                ]
                self.add_flow(datapath, 300, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, actions=actions
        )
        datapath.send_msg(mod)
        self.logger.info("Flow added to switch %s: match=%s, actions=%s", hex(datapath.id), match, actions)

    @set_ev_cls(ofp_event.EventOFPErrorMsg, [MAIN_DISPATCHER, CONFIG_DISPATCHER])
    def error_msg_handler(self, ev):
        msg = ev.msg
        self.logger.error('OFPErrorMsg received: type=0x%02x code=0x%02x message=%s',
                          msg.type, msg.code, msg.data)
