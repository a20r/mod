import networkx as nx
from osm import *
import geopy as geo
from geopy.distance import distance
import numpy as np

"""
This code has graciously been provided by the most honourable Aleksejs Sazonovs
"""


def make_weighted(G):
    """
    A method for converting NetworkX graph with geo positions into a weighted NetworkX graph. The distance between points is
    inversely proportional to the distance between points.
    :return: weighted network in NetworkX format, maximum distance between two nodes
    """
    G = max(nx.strongly_connected_component_subgraphs(G), key=len)
    # For each edge, put (geographical distance * -1) as its weight. Calculate the largest distance beteen nodes
    max_distance = 0
    for u, v, d in G.edges(data=True):
        u_point = geo.Point(G.node[u]['data'].lat, G.node[u]['data'].lon)
        v_point = geo.Point(G.node[v]['data'].lat, G.node[v]['data'].lon)
        closeness = distance(u_point,v_point).kilometers
        G[u][v]['weight'] = closeness

        if abs(closeness) > max_distance:
            max_distance = abs(closeness)

    return G, max_distance

def simplify_by_degree(G, max_distance):
    """
    Simplify the graph. Remove every node where degree=2 and connect their neighbour nodes, making the roads straight.
    Thus, rather than describing the structure of the road, the network describes its connectivity.
    :param G: NetworkX graph created by the osm2nx method
    :param max_distance: max distance between two nodes in the network. Asked as a parameter to avoid repetitive iteration
    :return: Simplified network in NetworkX format
    """
    G_simple = G
    for n in G_simple.nodes():
        if G_simple.in_degree(n) == 1 and G_simple.out_degree(n) == 1:
            weight_in_n = G[G.predecessors(n)[0]][n]['weight']
            weight_out_n = G[n][G.successors(n)[0]]['weight']
            weight_new = weight_in_n + weight_out_n
            G_simple.add_edge(G.predecessors(n)[0], G.successors(n)[0], weight=weight_new)
            G_simple.remove_node(n)

    return G_simple


def get_osm_graph(left, bottom, right, top):
    G = read_osm(download_osm(left, bottom, right, top))
    G, max_distance = make_weighted(G)
    G = simplify_by_degree(G, max_distance)
    return G


if __name__ == "__main__":
    G = read_osm(download_osm(-73.985076, 40.753528, -73.952211, 40.772996))
    G, max_distance = make_weighted(G)
    G = simplify_by_degree(G, max_distance)
    data = nx.all_pairs_shortest_path(G)
