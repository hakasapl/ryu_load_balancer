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
import os

class LoadBalancerTopo(Topo):
    """
    Load Balancer Custom Topology containing 3 slave nodes and 1 switch
    """

    internalGateway = "192.168.1.1"
    externalGateway = "128.128.128.1"

    ip_h1 = "192.168.1.11/24"
    ip_h2 = "192.168.1.12/24"
    ip_h3 = "192.168.1.13/24"

    ip_c1 = "128.128.128.11/24"
    ip_c2 = "128.128.128.12/24"
    ip_c3 = "128.128.128.13/24"

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        h1 = self.addHost('h1', ip=self.ip_h1)
        h2 = self.addHost('h2', ip=self.ip_h2)
        h3 = self.addHost('h3', ip=self.ip_h3)

        c1 = self.addHost('c1', ip=self.ip_c1)
        c2 = self.addHost('c2', ip=self.ip_c2)
        c3 = self.addHost('c3', ip=self.ip_c3)

        s1 = self.addSwitch('s1')
        
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

        self.addLink(c1, s1)
        self.addLink(c2, s1)
        self.addLink(c3, s1)

topo = LoadBalancerTopo()
net = Mininet(topo=topo, controller=RemoteController)
net.start()
dumpNodeConnections(net.hosts)

# Create Bridge Interfaces
stream = os.popen('./bridge_setup.sh')
print(stream.read())

# Add Default Routes for all the nodes
h1, h2, h3, c1, c2, c3 = net.get('h1', 'h2', 'h3', 'c1', 'c2', 'c3')
h1.cmd("ip route add default via " + LoadBalancerTopo.internalGateway)
h2.cmd("ip route add default via " + LoadBalancerTopo.internalGateway)
h3.cmd("ip route add default via " + LoadBalancerTopo.internalGateway)
c1.cmd("ip route add default via " + LoadBalancerTopo.externalGateway)
c2.cmd("ip route add default via " + LoadBalancerTopo.externalGateway)
c3.cmd("ip route add default via " + LoadBalancerTopo.externalGateway)

CLI(net)  # hang here until user closes the CLI

# Destroy the bridges once its done
stream = os.popen('./bridge_destroy.sh')
print(stream.read())

net.stop()  # stop mininet