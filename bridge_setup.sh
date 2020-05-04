#!/bin/bash

#Miniet creates a bridge by default using the switch name.
#So we delete and re-create our own bridges in the next step   
ovs-vsctl del-br s1

#Create bridge OVS1 
ovs-vsctl add-br OVS1
#Associate interface s1-eth2(server) to OVS1 
ovs-vsctl add-port OVS1 s1-eth2 


#Create bridge OVS2
ovs-vsctl add-br OVS2
#Associate interface s1-eth1(client) to OVS2
ovs-vsctl add-port OVS2 s1-eth1

#Assign IP addresses to the interfaces of the respective bridges
ifconfig OVS1 128.128.128.1/24 up
ifconfig OVS2 10.0.0.1/24 up

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
ovs-ofctl add-flow OVS2 in_port=1,actions=65534
ovs-ofctl add-flow OVS2 in_port=65534,actions=output:1