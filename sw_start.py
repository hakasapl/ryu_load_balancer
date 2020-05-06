#!/usr/bin/python3
""" Custom topology example

One switch with server and client on either side:

   host --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

class SimpleSwitchTopo(Topo):
    """
    Simple switch topology for testing direct connection without a load balancer
    """

    ip_h1 = "192.168.1.11/24"
    ip_h0 = "192.168.1.1/24"
    ip_c1 = "192.168.1.12/24"

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        h0 = self.addHost('h0', ip=self.ip_h0)
        h1 = self.addHost('h1', ip=self.ip_h1)
        c1 = self.addHost('c1', ip=self.ip_c1)

        s1 = self.addSwitch('s1')
        
        # Add links
        self.addLink(h0, s1)
        self.addLink(h1, s1)
        self.addLink(c1, s1)

topo = SimpleSwitchTopo()
net = Mininet(topo=topo, controller=RemoteController)
net.start()

dumpNodeConnections(net.hosts)

CLI(net)  # hang here until user closes the CLI

net.stop()  # stop mininet