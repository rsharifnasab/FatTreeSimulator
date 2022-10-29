#!/usr/bin/python3

from sys import argv

import networkx as nx

# K racks switches links
test_cases = [
    (4,  16,    20,      48),
    (8,  128,   80,      384),
    (16, 1024,  320,     3_072),
    (24, 3_456,  720,    10_368),
    (32, 8_192,  1_280,  24_576),
    (48, 27_648, 2_880,  82_944),
]

K = int(argv[1])
K = 8


pod_count = K
switch_per_pod = K
switch_port_count = K


k2 = K // 2
edge_sw_per_pod = k2
aggr_sw_per_pod = k2

k2p2 = (K//2) * (K//2)
server_per_pod =  k2p2
core_switch_count =  k2p2

total_server_count = pod_count * server_per_pod
assert total_server_count == (K**3)/4

total_switch_count = core_switch_count + pod_count * switch_per_pod
assert total_switch_count == (5 * (K**2)) // 4

total_link_count = core_switch_count*pod_count \
        + aggr_sw_per_pod * edge_sw_per_pod * pod_count \
        + total_server_count
assert total_link_count == (3 * (K**3)) // 4

for k, racks, switches, links in test_cases:
    assert racks == (k**3)//4
    assert switches == 5 * (k**2) // 4
    assert links == (3 * (k**3)) //4




G = nx.Graph()


for i in range(core_switch_count):
    G.add_node(f"core {i}")


