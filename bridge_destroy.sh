#!/bin/bash

# Delete remaining bridges

ovs-vsctl --if-exists del-br OVS1
ovs-vsctl --if-exists del-br OVS2