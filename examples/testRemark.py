from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time

def topology():
    net = Mininet(controller=Controller, switch=OVSSwitch)

    info('*** Adding Controller\n')
    net.addController('c0')

    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')

    info('*** Adding switch\n')
    s1 = net.addSwitch('s1')

    info('*** Creating links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    info('*** Starting network\n')
    net.start()

    # Configure QoS on s1
    s1.cmd('ovs-vsctl set Port s1-eth1 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=10000000 queues=0=@q0 -- --id=@q0 create Queue other-config:min-rate=5000000 other-config:max-rate=10000000 other-config:priority=1')

    # Add flow rule to set DSCP field
    s1.cmd('ovs-ofctl add-flow s1 priority=65535,ip,nw_src=10.0.0.1,actions=set_field:0x1a->ip_dscp,output:2')

    # Start tcpdump on h2 to capture packets
    h2.cmd('tcpdump -n -i h2-eth0 ip -v -c 10 > /tmp/h2_tcpdump.txt &')

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
