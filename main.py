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


def check_test_cases(given_test_cases):
    for k, racks, switches, links in given_test_cases:
        assert racks == (k**3)//4
        assert switches == 5 * (k**2) // 4
        assert links == (3 * (k**3)) // 4


def save_to_csv(G):
    # TODO: more efficient way to do this
    df = pd.DataFrame({"node1": [], "node2": [], "num": []})
    for n1name, n2name in G.edges():
        n1 = G.nodes[n1name]["num"]
        n2 = G.nodes[n2name]["num"]
        df.loc[len(df.index)] = [n1, n2, 0]
    df.to_csv("result.csv", index=False)


def add_nodes(G):

    cnt = 0
    for i in range(total_server_count):
        G.add_node(f"server {i}", num = cnt)
        cnt += 1

    for i in range(edge_sw_per_pod * pod_count):
        G.add_node(f"edge {i}", num = cnt)
        cnt += 1

    for i in range(aggr_sw_per_pod * pod_count):
        G.add_node(f"aggr {i}", num = cnt)
        cnt += 1

    for i in range(core_switch_count):
        G.add_node(f"core {i}", num = cnt)
        cnt += 1


    assert G.number_of_nodes() == total_server_count + total_switch_count


def draw(G):
    subax2 = plt.subplot(122)
    nx.draw(G, pos=nx.circular_layout(G), node_color='r', edge_color='b')
    plt.savefig("img.png")


def formulas(K):
    global pod_count, switch_per_pod, switch_port_count

    pod_count = K
    switch_per_pod = K
    switch_port_count = K

    global k2, edge_sw_per_pod, aggr_sw_per_pod, server_per_edge_switch
    k2 = K // 2
    edge_sw_per_pod = k2
    aggr_sw_per_pod = k2
    server_per_edge_switch = k2

    global k2p2, server_per_pod, core_switch_count
    k2p2 = (K//2) * (K//2)
    server_per_pod = k2p2
    core_switch_count = k2p2

    global total_server_count, total_switch_count, total_link_count
    total_server_count = pod_count * server_per_pod
    assert total_server_count == (K**3)//4

    total_switch_count = core_switch_count + pod_count * switch_per_pod
    assert total_switch_count == (5 * (K**2)) // 4

    total_link_count = core_switch_count*pod_count \
        + aggr_sw_per_pod * edge_sw_per_pod * pod_count \
        + total_server_count
    assert total_link_count == (3 * (K**3)) // 4


def assertions(G):
    servers = [n for n in G.nodes(data=False) if "server" in n]
    edge_sw = [n for n in G.nodes(data=False) if "edge" in n]
    aggr_sw = [n for n in G.nodes(data=False) if "aggr" in n]
    core_sw = [n for n in G.nodes(data=False) if "core" in n]

    for server in servers:
        assert len(list(G.neighbors(server))) == 1

    for switch in edge_sw + aggr_sw + core_sw:
        #print(f"aggr sw {switch} - {list(G.neighbors(switch))}")
        assert len(list(G.neighbors(switch))) == switch_port_count

    assert G.number_of_nodes() == total_server_count + total_switch_count
    assert len(core_sw) == core_switch_count
    assert len(servers) == total_server_count
    assert len(edge_sw) == edge_sw_per_pod * pod_count
    assert len(aggr_sw) == aggr_sw_per_pod * pod_count


def add_edges(G):
    cnt = 0
    for i in range(edge_sw_per_pod * pod_count):
        for _ in range(server_per_edge_switch):
            G.add_edge(f"edge {i}", f"server {cnt}")
            cnt += 1

    for pod_no in range(pod_count):
        for i in range(aggr_sw_per_pod):
            for j in range(edge_sw_per_pod):
                aggr = pod_no * aggr_sw_per_pod + i
                edge = pod_no * edge_sw_per_pod + j
                G.add_edge(f"aggr {aggr}", f"edge {edge}")

    aggr_no = 0
    cur_aggr_cons = 0
    for pod_no in range(pod_count):
        for core_router_no in range(core_switch_count):
            G.add_edge(f"aggr {aggr_no}", f"core {core_router_no}")
            cur_aggr_cons += 1
            if cur_aggr_cons == switch_port_count//2:
              aggr_no += 1
              cur_aggr_cons = 0


def main():
    if len(argv) < 2:
        print("not enough arguments")
        return

    command = argv[1]
    if command == "test":
        check_test_cases(test_cases)
        return

    K = int(command)
    assert K % 2 == 0

    formulas(K)

    G = nx.Graph()
    add_nodes(G)
    add_edges(G)
    assertions(G)
    save_to_csv(G)
    draw(G)


if __name__ == "__main__":
    main()
