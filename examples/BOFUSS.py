from mininet.node import CPULimitedHost, RemoteController
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import Node

class BOFUSSSwitch(Node):
    """Custom Switch class for BOFUSS."""
    def __init__(self, name, dpid=None, **kwargs):
        super(BOFUSSSwitch, self).__init__(name, **kwargs)
        self.dpid = dpid
        self.listenPort = kwargs.get('listenPort', 6633)  # Default OpenFlow port

    def start(self, controllers):
        """Start BOFUSS datapath and secure channel."""
        interfaces = ','.join(self.intfNames())
        # Start the datapath
        self.cmd('udatapath/ofdatapath --datapath-id=%s --interfaces=%s ptcp:%s &' % (self.dpid, interfaces, self.listenPort))
        # Assuming there's one controller
        if controllers:
            controller = controllers[0]
            self.cmd('secchan/ofprotocol tcp:%s:%s tcp:%s:%s &' % (self.IP(), self.listenPort, controller.IP(), controller.port))

    def stop(self):
        """Stop BOFUSS process."""
        self.cmd('kill %udatapath')
        self.cmd('kill %secchan')

class SimplePktSwitch(Topo):
    """Simple topology example."""
    def __init__(self, **opts):
        """Create custom topo."""
        super(SimplePktSwitch, self).__init__(**opts)
        # Add hosts and switches (code remains the same as your original script)

        # Add links (code remains the same as your original script)

def run():
    c = RemoteController('c', '127.0.0.1', port=6653)
    net = Mininet(topo=SimplePktSwitch(), host=CPULimitedHost, switch=BOFUSSSwitch, controller=None)
    net.addController(c)
    net.start()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('debug')
    run()
