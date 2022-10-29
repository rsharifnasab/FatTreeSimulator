#!/usr/bin/env python3

from sys import argv

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

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
assert K % 2 == 0


pod_count = K
switch_per_pod = K
switch_port_count = K


k2 = K // 2
edge_sw_per_pod = k2
aggr_sw_per_pod = k2
server_per_edge_switch = k2

k2p2 = (K//2) * (K//2)
server_per_pod =  k2p2
core_switch_count =  k2p2

total_server_count = pod_count * server_per_pod
assert total_server_count == (K**3)//4

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


for i in range(aggr_sw_per_pod * pod_count):
    G.add_node(f"aggr {i}")

for i in range(edge_sw_per_pod * pod_count):
    G.add_node(f"edge {i}")

for i in range(total_server_count):
    G.add_node(f"server {i}")

assert G.number_of_nodes() == total_server_count + total_switch_count


cnt = 0
for i in range(edge_sw_per_pod * pod_count):
    for _ in range(server_per_edge_switch):
        G.add_edge(f"edge {i}", f"server {cnt}")
        cnt+= 1


for pod_no in range(pod_count):
    for i in range(aggr_sw_per_pod):
        for j in range(edge_sw_per_pod):
            aggr = pod_no * aggr_sw_per_pod + i
            edge = pod_no * edge_sw_per_pod + j
            G.add_edge(f"aggr {aggr}", f"edge {edge}")



# TODO: connect core to aggr nodes

servers = [ n for  n in G.nodes(data=False) if "server" in n ]
edge_sw = [ n for  n in G.nodes(data=False) if "edge" in n ]
aggr_sw = [ n for  n in G.nodes(data=False) if "aggr" in n ]
core_sw = [ n for  n in G.nodes(data=False) if "core" in n ]

for server in servers:
    assert len(list(G.neighbors(server))) == 1

for switch in edge_sw : #aggr_sw + core_sw + edge_sw:
    assert len(list(G.neighbors(switch))) == switch_port_count

assert G.number_of_nodes() == total_server_count + total_switch_count


subax2 = plt.subplot(122)
nx.draw(G, pos=nx.circular_layout(G), node_color='r', edge_color='b')

plt.savefig("img.png")


# TODO: more efficient way to do this
df = pd.DataFrame({"node1":[], "node2":[], "num":[]})

for n1, n2 in G.edges():
    df.loc[len(df.index)] = [n1, n2, 0]




df.to_csv("result.csv", index=False)
