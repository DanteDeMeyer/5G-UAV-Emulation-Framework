#!/usr/bin/python

from mininet.node import RemoteController, OVSKernelSwitch, Host
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
from subprocess import call
from mn_wifi.telemetry import telemetry

import random
import time
import threading
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def circular_movement(center, radius, angle, height):
    x_center, y_center, z_center = center
    x_new = x_center + radius * math.cos(angle)
    y_new = y_center + radius * math.sin(angle)
    z_new = height
    return [x_new, y_new, z_new]

def update_positions(net, stations, radius, interval, min_height, max_height, center_positions):
    angle = 0
    angle_increment = math.pi / 30  # Incremental angle for circular movement

    while True:
        height = random.uniform(min_height, max_height)
        for i, sta in enumerate(stations):
            center = center_positions[i]
            new_position = circular_movement(center, radius, angle, height)
            new_position_str = ','.join(map(str, new_position))  # Convert list to a comma-separated string
            net.mobility(sta, 'start', time=int(time.time()), position=new_position_str)
            net.mobility(sta, 'stop', time=int(time.time()) + interval, position=new_position_str)
            sta.params['position'] = new_position  # Update the position
        angle += angle_increment
        time.sleep(interval)

def myNetwork():

    net = Mininet_wifi(topo=None,
                       build=False,
                       link=wmediumd,
                       wmediumd_mode=interference,
                       ipBase='10.0.0.0/8')

    info('*** Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           port=6634,
                           ip='127.0.0.1')

    info('*** Adding CN and BBUs\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow10', dpid='0000000000000001')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow10', dpid='0000000000000002')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, protocols='OpenFlow10', dpid='0000000000000003')

    info('*** Adding RRHs\n')
    ap1 = net.addAccessPoint('ap1', cls=OVSKernelAP, ssid='ap1-ssid',
                             channel='1', mode='g', position='52.0,445.0,0',
                             protocols='OpenFlow10', passwd='123456789a',
                             encrypt='wpa2', datapath='user', dpid='0000000000001001')
    ap2 = net.addAccessPoint('ap2', cls=OVSKernelAP, ssid='ap2-ssid',
                             channel='6', mode='g', position='335.0,435.0,0',
                             protocols='OpenFlow10', passwd='123456789a',
                             encrypt='wpa2', datapath='user', dpid='0000000000001002')
    ap3 = net.addAccessPoint('ap3', cls=OVSKernelAP, ssid='ap3-ssid',
                             channel='11', mode='g', position='583.0,445.0,0',
                             protocols='OpenFlow10', passwd='123456789a',
                             encrypt='wpa2', datapath='user', dpid='0000000000001003')
    ap4 = net.addAccessPoint('ap4', cls=OVSKernelAP, ssid='ap4-ssid',
                             channel='1', mode='g', position='824.0,454.0,0',
                             protocols='OpenFlow10', passwd='123456789a',
                             encrypt='wpa2', datapath='user', dpid='0000000000001004')

    info('*** Adding server\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.9', defaultRoute=None)

    info('*** Adding UAVs\n')
    bgscan_config = {
        'bgscan_threshold': -60,  # Threshold for signal strength to trigger a scan
        's_interval': 5,  # Interval for short scans (in seconds)
        'l_interval': 10,  # Interval for long scans (in seconds)
        'bgscan_module': 'simple'  # Background scanning module
    }
    sta1 = net.addStation('dr1', ip='10.0.0.1', position='52.0,575.0,0', min_x=0, min_y=0, max_x=1000, max_y=1000, **bgscan_config)
    sta2 = net.addStation('dr2', ip='10.0.0.2', position='335.0,575.0,0', min_x=0, min_y=0, max_x=1000, max_y=1000, **bgscan_config)
    sta3 = net.addStation('dr3', ip='10.0.0.3', position='287.0,575.0,0', min_x=0, min_y=0, max_x=1000, max_y=1000, **bgscan_config)
    sta4 = net.addStation('dr4', ip='10.0.0.4', position='369.0,579.0,0', min_x=0, min_y=0, max_x=1000, max_y=1000, **bgscan_config)
    sta5 = net.addStation('dr5', ip='10.0.0.5', position='531.0,580.0,0', min_x=0, min_y=0, max_x=1000, max_y=1000, **bgscan_config)
    sta6 = net.addStation('dr6', ip='10.0.0.6', position='613.0,578.0,0', min_x=0, min_y=0, max_x=1000, max_y=1000, **bgscan_config)
    sta7 = net.addStation('dr7', ip='10.0.0.7', position='797.0,572.0,0', min_x=0, min_y=0, max_x=1000, max_y=1000, **bgscan_config)
    sta8 = net.addStation('dr8', ip='10.0.0.8', position='824.0,305.0,0', min_x=0, min_y=0, max_x=1000, max_y=1000, **bgscan_config)
    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring 5G network\n")
    net.configureWifiNodes()

    info('*** Add links\n')
    net.addLink(sta3, ap1)
    net.addLink(sta4, ap2)
    net.addLink(sta5, ap3)
    net.addLink(sta6, ap3)
    net.addLink(sta7, ap4)
    net.addLink(sta8, ap4)
    net.addLink(s2, ap4)
    net.addLink(s2, ap3)
    net.addLink(s1, ap2)
    net.addLink(s1, ap1)
    net.addLink(s3, s1)
    net.addLink(s3, s2)
    net.addLink(s3, h1)

    nodes = net.stations + net.aps
    telemetry(nodes=nodes, single=True, data_type='position', min_x=0, min_y=0, max_x=1000, max_y=1000)
    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting CN and RAN\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('ap1').start([c0])
    net.get('ap2').start([c0])
    net.get('ap3').start([c0])
    net.get('ap4').start([c0])

    info('*** Configuring mobility with handover\n')
    radius = 20  # Radius for circular movement
    min_height, max_height = 10, 15  # Height range for UAVs
    interval = 0.1  # Smaller interval for more frequent updates

    stations = [sta3, sta4, sta5, sta6, sta7, sta8]
    center_positions = [ap.params['position'] for ap in [ap1, ap2, ap3, ap3, ap4, ap4]]
    for sta in stations:
        sta.params['position'] = sta.position

    threading.Thread(target=update_positions, args=(net, stations, radius, interval, min_height, max_height, center_positions), daemon=True).start()
    info('*** Post configure nodes\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
