#!/usr/bin/python

from mininet.node import Controller, OVSKernelSwitch,  Host
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
from subprocess import call


def myNetwork():

    net = Mininet_wifi(topo=None,
                       build=False,
                       link=wmediumd,
                       wmediumd_mode=interference,
                       ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0 = net.addController(name='c0',
                           controller=Controller,
                           protocol='tcp',
                           port=6653)

    info( '*** Add switches/APs\n')
    ap1 = net.addAccessPoint('ap1', cls=OVSKernelAP, ssid='ap1-ssid',
                             channel='1', mode='g', position='229.0,290.0,0')
    ap2 = net.addAccessPoint('ap2', cls=OVSKernelAP, ssid='ap2-ssid',
                             channel='1', mode='g', position='467.0,291.0,0')
    ap3 = net.addAccessPoint('ap3', cls=OVSKernelAP, ssid='ap3-ssid',
                             channel='1', mode='g', position='725.0,308.0,0')
    ap4 = net.addAccessPoint('ap4', cls=OVSKernelAP, ssid='ap4-ssid',
                             channel='1', mode='g', position='969.0,317.0,0')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)

    info( '*** Add hosts/stations\n')
    sta1 = net.addStation('sta1', ip='10.0.0.1',
                           position='164.0,462.0,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2',
                           position='268.0,459.0,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3',
                           position='421.0,459.0,0')
    sta4 = net.addStation('sta4', ip='10.0.0.4',
                           position='516.0,454.0,0')
    sta5 = net.addStation('sta5', ip='10.0.0.5',
                           position='675.0,458.0,0')
    sta6 = net.addStation('sta6', ip='10.0.0.6',
                           position='784.0,459.0,0')
    sta7 = net.addStation('sta7', ip='10.0.0.7',
                           position='929.0,461.0,0')
    sta8 = net.addStation('sta8', ip='10.0.0.8',
                           position='1019.0,461.0,0')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.9', defaultRoute=None)

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)
    net.addLink(sta3, ap2)
    net.addLink(sta4, ap2)
    net.addLink(sta5, ap3)
    net.addLink(sta6, ap3)
    net.addLink(sta7, ap4)
    net.addLink(sta8, ap4)
    net.addLink(ap1, s1)
    net.addLink(ap2, s1)
    net.addLink(ap3, s2)
    net.addLink(ap4, s2)
    net.addLink(s1, s3)
    net.addLink(s2, s3)
    net.addLink(s3, h1)

    net.plotGraph(max_x=1000, max_y=1000)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches/APs\n')
    net.get('ap1').start([])
    net.get('ap2').start([])
    net.get('ap3').start([])
    net.get('ap4').start([])
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])

    info( '*** Post configure nodes\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'debug' )
    myNetwork()

