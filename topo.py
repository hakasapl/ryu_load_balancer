from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.util import dumpNodeConnections


class LoadBalancerTopo(Topo):
    """
    Load Balancer Custom Topology containing 3 slave nodes and 1 switch
    """

    ip_h1 = "10.0.1.1/24"
    ip_h2 = "10.0.1.2/24"
    ip_h3 = "10.0.1.3/24"
    ip_c1 = "10.0.0.10"

    ip_ext = "128.128.128.2"

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        h1 = self.addHost('h1', ip=self.ip_h1)
        h2 = self.addHost('h2', ip=self.ip_h2)
        h3 = self.addHost('h3', ip=self.ip_h3)
        s1 = self.addSwitch('s1')
        c1 = self.addHost('c1', ip=self.ip_c1)

        ext = self.addHost('ext', ip=self.ip_ext)

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(ext, s1)


topos = {'loadbalancertopo': (lambda: LoadBalancerTopo())}
