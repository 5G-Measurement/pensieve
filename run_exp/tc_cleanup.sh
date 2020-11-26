#!/usr/bin/env bash
# @author: Arvind Narayanan

interface="virbr0"
latency=54
port1=6001
port2=6002

# Clean up
sudo modprobe -r ifb
sudo tc qdisc del dev $interface ingress
# sudo ip link set dev $interface down
echo "Finished cleaning"