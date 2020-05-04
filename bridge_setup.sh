#!/bin/bash

#
# This script will only work for the topology it was specifically designed for
#

#Miniet creates a bridge by default using the switch name.
#So we delete and re-create our own bridges in the next step   
ovs-vsctl --if-exists del-br s1

#Create bridge OVS1 (Client Bridge - Public Internet)
ovs-vsctl add-br OVS1
ovs-vsctl add-port OVS1 s1-eth4
ovs-vsctl add-port OVS1 s1-eth5
ovs-vsctl add-port OVS1 s1-eth6

#Create bridge OVS2 (Private Bridge - Load Balancer Net)
ovs-vsctl add-br OVS2
ovs-vsctl add-port OVS2 s1-eth1
ovs-vsctl add-port OVS2 s1-eth2
ovs-vsctl add-port OVS2 s1-eth3

#Assign IP addresses to the interfaces of the respective bridges
ifconfig OVS1 128.128.128.1/24 up
ifconfig OVS2 192.168.1.1/24 up

#Delete any previous flows
ovs-ofctl del-flows OVS1
ovs-ofctl del-flows OVS2

#Connect OVS1 bridge to the SDN Controller
ovs-vsctl set-controller OVS1 tcp:127.0.0.1:6653

#Add flows to bridge OVS2. 65534 indicates local interface(lo).
#If in_port is 1, out_port will be its local interface and vice-versa.
#The following steps ensures connectivity between OVS1 and OVS2.
#Default routes are set on OVS2 and OVS1 is used to connect to the RYU SDN Controller.
#The NAT functionality is implemented on Controller. 
ovs-ofctl add-flow OVS2 in_port=1,actions=LOCAL
ovs-ofctl add-flow OVS2 in_port=LOCAL,actions=output:1