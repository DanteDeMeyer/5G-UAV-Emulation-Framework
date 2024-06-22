import gevent.monkey
gevent.monkey.patch_all()

import sys
from ryu.cmd import manager

if __name__ == "__main__":
    # Add the command-line arguments for the Ryu manager
    sys.argv.extend(['--ofp-tcp-listen-port', '20002', 'videoController.py'])
    manager.main()
