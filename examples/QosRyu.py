#!/usr/bin/python

from mininet.node import RemoteController, OVSKernelSwitch, Host
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def myNetwork():
    net = Mininet_wifi(topo=None,
                       build=False,
                       link=wmediumd,
                       wmediumd_mode=interference,
                       ipBase='10.0.0.0/8')

    info('*** Adding controller\n')
    fv = net.addController(name='fv',
                           controller=RemoteController,
                           ip='127.0.0.1',  # IP address of FlowVisor
                           port=6633)

    info('*** Add switches/APs\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, protocols='OpenFlow13')
    ap1 = net.addAccessPoint('ap1', cls=OVSKernelAP, ssid='ap1-ssid',
                             channel='1', mode='g', position='52.0,445.0,0', protocols='OpenFlow13')
    ap2 = net.addAccessPoint('ap2', cls=OVSKernelAP, ssid='ap2-ssid',
                             channel='1', mode='g', position='335.0,435.0,0', protocols='OpenFlow13')
    ap3 = net.addAccessPoint('ap3', cls=OVSKernelAP, ssid='ap3-ssid',
                             channel='1', mode='g', position='583.0,445.0,0', protocols='OpenFlow13')
    ap4 = net.addAccessPoint('ap4', cls=OVSKernelAP, ssid='ap4-ssid',
                             channel='1', mode='g', position='824.0,454.0,0', protocols='OpenFlow13')

    info('*** Add hosts/stations\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.9', defaultRoute=None)
    sta1 = net.addStation('sta1', ip='10.0.0.1', position='35.0,577.0,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2', position='110.0,578.0,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3', position='287.0,575.0,0')
    sta4 = net.addStation('sta4', ip='10.0.0.4', position='369.0,579.0,0')
    sta5 = net.addStation('sta5', ip='10.0.0.5', position='531.0,580.0,0')
    sta6 = net.addStation('sta6', ip='10.0.0.6', position='613.0,578.0,0')
    sta7 = net.addStation('sta7', ip='10.0.0.7', position='797.0,572.0,0')
    sta8 = net.addStation('sta8', ip='10.0.0.8', position='886.0,576.0,0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info('*** Add links\n')
    net.addLink(sta1, ap1)
    net.addLink(ap1, sta2)
    net.addLink(sta4, ap2)
    net.addLink(sta3, ap2)
    net.addLink(ap3, sta5)
    net.addLink(ap3, sta6)
    net.addLink(ap4, sta7)
    net.addLink(ap4, sta8)
    net.addLink(s2, ap4)
    net.addLink(s2, ap3)
    net.addLink(s1, ap2)
    net.addLink(s1, ap1)
    net.addLink(s3, s1)
    net.addLink(s3, s2)
    net.addLink(s3, h1)

    net.plotGraph(max_x=1000, max_y=1000)

    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches/APs\n')
    net.get('s1').start([fv])
    net.get('s2').start([fv])
    net.get('s3').start([fv])
    net.get('ap1').start([fv])
    net.get('ap2').start([fv])
    net.get('ap3').start([fv])
    net.get('ap4').start([fv])

    info('*** Post configure nodes\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
