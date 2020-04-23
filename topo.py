from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.util import dumpNodeConnections


class LoadBalancerTopo(Topo):
    """
    Load Balancer Custom Topology containing 3 slave nodes and 1 switch
    """

    ip_h1 = "10.0.1.1"
    ip_h2 = "10.0.1.2"
    ip_h3 = "10.0.1.3"

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        h1 = self.addHost('h1', ip=self.ip_h1)
        h2 = self.addHost('h2', ip=self.ip_h2)
        h3 = self.addHost('h3', ip=self.ip_h3)
        s1 = self.addSwitch('s1')

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)


topos = {'loadbalancertopo': (lambda: LoadBalancerTopo())}
