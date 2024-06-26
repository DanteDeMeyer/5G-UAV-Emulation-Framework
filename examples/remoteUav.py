#!/usr/bin/python

from mininet.node import RemoteController, OVSKernelSwitch,  Host
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
                           controller=RemoteController,
                           protocol='tcp',
                           port=6633,
			   ip='127.0.0.1')

    info( '*** Add switches/APs\n')
    s1 = net.addSwitch('bbu1', cls=OVSKernelSwitch, protocols = 'OpenFlow13')
    s2 = net.addSwitch('bbu2', cls=OVSKernelSwitch, protocols = 'OpenFlow13')
    s3 = net.addSwitch('cn', cls=OVSKernelSwitch, protocols = 'OpenFlow13')
    ap1 = net.addAccessPoint('rrh1', cls=OVSKernelAP, ssid='rrh1-ssid',
                             channel='1', mode='g', position='52.0,445.0,0', protocols = 'OpenFlow13')
    ap2 = net.addAccessPoint('rrh2', cls=OVSKernelAP, ssid='rrh2-ssid',
                             channel='1', mode='g', position='335.0,435.0,0', protocols = 'OpenFlow13')
    ap3 = net.addAccessPoint('rrh3', cls=OVSKernelAP, ssid='rrh3-ssid',
                             channel='1', mode='g', position='583.0,445.0,0', protocols = 'OpenFlow13')
    ap4 = net.addAccessPoint('rrh4', cls=OVSKernelAP, ssid='rrh4-ssid',
                             channel='1', mode='g', position='824.0,454.0,0', protocols = 'OpenFlow13')

    info( '*** Add hosts/stations\n')
    h1 = net.addHost('server', cls=Host, ip='10.0.0.9', defaultRoute=None)
    sta1 = net.addStation('dr1', mac='00:00:00:00:00:01', ip='10.0.0.1',
                           position='35.0,577.0,0')
    sta2 = net.addStation('dr2', mac='00:00:00:00:00:02', ip='10.0.0.2',
                           position='110.0,578.0,0')
    sta3 = net.addStation('dr3', mac='00:00:00:00:00:03', ip='10.0.0.3',
                           position='287.0,575.0,0')
    sta4 = net.addStation('dr4', mac='00:00:00:00:00:04', ip='10.0.0.4',
                           position='369.0,579.0,0')
    sta5 = net.addStation('dr5', mac='00:00:00:00:00:05', ip='10.0.0.5',
                           position='531.0,580.0,0')
    sta6 = net.addStation('dr6', mac='00:00:00:00:00:06', ip='10.0.0.6',
                           position='613.0,578.0,0')
    sta7 = net.addStation('dr7', mac='00:00:00:00:00:07', ip='10.0.0.7',
                           position='797.0,572.0,0')
    sta8 = net.addStation('dr8', mac='00:00:00:00:00:08', ip='10.0.0.8',
                           position='886.0,576.0,0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
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

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches/APs\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('ap1').start([c0])
    net.get('ap2').start([c0])
    net.get('ap3').start([c0])
    net.get('ap4').start([c0])

    info( '*** Post configure nodes\n')

    nodes = net.stations
    telemetry(nodes=nodes, single=True, data_type='position')

    sta_drone = []
    for n in net.stations:
        sta_drone.append(n.name)
    sta_drone_send = ' '.join(map(str, sta_drone))

    info("*** Starting Socket Server\n")
    net.socketServer(ip='127.0.0.1', port=12345)

    info("*** Starting CoppeliaSim\n")
    path = os.path.dirname(os.path.abspath(__file__))
    os.system('{}/CoppeliaSim_Edu_V4_1_0_Ubuntu/coppeliaSim.sh -s {}'
              '/simulation.ttt -gGUIITEMS_2 &'.format(path, path))
    time.sleep(10)

    info("*** Perform a simple test\n")
    simpleTest = 'python {}/simpleTest.py '.format(path) + sta_drone_send + ' &'
    os.system(simpleTest)

    time.sleep(5)

    info("*** Configure the node position\n")
    setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    os.system(setNodePosition)

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping Network")
    kill_process()
    net.stop()

def kill_process():
    os.system('pkill -9 -f coppeliaSim')
    os.system('pkill -9 -f simpleTest.py')
    os.system('pkill -9 -f setNodePosition.py')
    os.system('rm examples/uav/data/*')

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

