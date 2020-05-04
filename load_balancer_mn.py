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

    internalGateway = "10.0.0.1"
    externalGateway = "128.128.128.1"

    ip_h1 = "10.0.0.11/24"
    ip_h2 = "10.0.0.12/24"
    ip_h3 = "10.0.0.13/24"

    ip_ext = "128.128.128.10"

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        h1 = self.addHost('h1', ip=self.ip_h1)
        h2 = self.addHost('h2', ip=self.ip_h2)
        h3 = self.addHost('h3', ip=self.ip_h3)
        s1 = self.addSwitch('s1')

        ext = self.addHost('ext', ip=self.ip_ext)

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(ext, s1)

topo = LoadBalancerTopo()
net = Mininet(topo=topo, controller=RemoteController)
net.start()
dumpNodeConnections(net.hosts)

# Create Bridge Interfaces
stream = os.popen('./bridge_setup.sh')
print(stream.read())

# Add Default Routes for all the nodes
h1, h2, h3, ext = net.get('h1', 'h2', 'h3', 'ext')
h1.cmd("ip route add default via " + LoadBalancerTopo.internalGateway)
h2.cmd("ip route add default via " + LoadBalancerTopo.internalGateway)
h3.cmd("ip route add default via " + LoadBalancerTopo.internalGateway)
ext.cmd("ip route add default via " + LoadBalancerTopo.externalGateway)

CLI(net)

# Destroy the bridges once its done
stream = os.popen('./bridge_destroy.sh')
print(stream.read())