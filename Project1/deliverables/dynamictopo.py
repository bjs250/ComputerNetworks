#!/usr/bin/python
                                                    

# CS6250 Computer Networks Project 1
# Creates a dynamic topology based on command line parameters and starts the Mininet Command Line Interface.

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, output, setLogLevel
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
import argparse
import sys
import os

# Parse Command Line Arguments
parser = argparse.ArgumentParser(description="Dynamic Topologies")
parser.add_argument('--delay',
                    help="Latency of network links, in ms",
                    required=True)

parser.add_argument('--bw',
                    type=int,
                    help=("Bandwidth of the links in Mbps."
                    "Must be >= 1"),
                    required=True)

parser.add_argument('--z',
                    type=int,
                    help=("Number of zones to create."
                    "Must be >= 1"),
                    required=True)

parser.add_argument('--n',
                    type=int,
                    help=("Number of hosts to create in each zone."
                    "Must be >= 1"),
                    required=True)

args = parser.parse_args()

lg.setLogLevel('info')

# Topology to be instantiated in Mininet
class DynamicTopo(Topo):
    "Dynamic Topology"

    def __init__(self, n=1, delay='1ms', z=1, bw=1, cpu=.1, max_queue_size=None, **params):
        """Ring topology with z zones.
        n: number of hosts per zone
        cpu: system fraction for each host
        bw: link bandwidth in Mb/s
        delay: link latency (e.g. 10ms)"""
        self.z = z
        self.n = n
        self.cpu = cpu
        self.bw = bw
        self.delay = delay

        self.max_queue_size = max_queue_size
        self.params = params

        # Initialize topo
        Topo.__init__(self, **params)

        # Host and link configuration
        hostConfig = {'cpu': self.cpu}
        linkConfig = {'bw': self.bw, 'delay': self.delay, 'loss': 0,
                   'max_queue_size': self.max_queue_size }

        #TODO: Create your Dynamic Mininet Topology here!
        #NOTE: You MUST label switches as s1, s2, ... sz
        #NOTE: You MUST label hosts as h1-1, h1-2, ... hz-n     
        #HINT: Use a loop to construct the topology in pieces.
        
        # Store switches and nodes in a dict
        switches = {}
        hosts = {}

        # construct hosts, switches, add links between hosts and switches
        for zone in range(1, self.z+1): # for 1-indexing
            
            # Construct switch
            switchname = 's' + str(zone)
            switches[switchname] = self.addSwitch(switchname)

            switch_port = 1
            for node in range(1, n+1): # for 1-indexing
                
                # Construct host
                hostname = 'h' + str(zone) + '-' + str(node)
                #hostname = 'h' + str(zone) + str(node) # no dash
                hosts[hostname] = self.addHost(hostname, **hostConfig)

                # Link host to switch
                self.addLink(hosts[hostname], switches[switchname], port1=0, port2=switch_port, **linkConfig)
                switch_port += 1

        # add links between zone switches
        for zone in range(1, self.z+1): # for 1-indexing
            if zone != z:
                current_switch = 's' + str(zone)
                next_switch = 's' + str(zone + 1)
            else:
                current_switch = 's' + str(zone)
                next_switch = 's' + str(1)
            self.addLink(switches[current_switch], switches[next_switch], port1=switch_port, port2=switch_port+1, **linkConfig)
                
        
def main():
    "Create specified topology and launch the command line interface"    
    topo = DynamicTopo(n=args.n, delay=args.delay, z=args.z, bw=args.bw)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    
    #TODO: Since this topology contains a cycle, we must enable the Spanning Tree Protocol (STP) on each switch.
    #      This is done with the following line of code: s1.cmd('ovs-vsctl set bridge s1 stp-enable=true')
    #      Here, you will need to generate this line of code for each switch.
    #HINT: You will need to get the switch objects from the net object defined above.

    for zone in range(1, topo.z+1): # for 1-indexing    
        switchname = 's' + str(zone)
        s = net.get(switchname)
        s.cmd('ovs-vsctl set bridge ' + switchname + ' stp-enable=true')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()