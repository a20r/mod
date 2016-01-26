
import geopy as geo
from geopy.distance import distance

"""
This code has graciously been provided by the most honourable Aleksejs Sazonovs
"""


def make_weighted(G):
    max_distance = 0
    for u, v, d in G.edges(data=True):
        u_point = geo.Point(G.node[u]['data'].lat, G.node[u]['data'].lon)
        v_point = geo.Point(G.node[v]['data'].lat, G.node[v]['data'].lon)
        closeness = distance(u_point, v_point).kilometers
        G[u][v]['weight'] = closeness

        if abs(closeness) > max_distance:
            max_distance = abs(closeness)

    return G, max_distance


def simplify_by_degree(G, max_distance):
    G_simple = G
    for n in G_simple.nodes():
        if G_simple.in_degree(n) == 1 and G_simple.out_degree(n) == 1:
            weight_in_n = G[G.predecessors(n)[0]][n]['weight']
            weight_out_n = G[n][G.successors(n)[0]]['weight']
            weight_new = weight_in_n + weight_out_n
            G_simple.add_edge(G.predecessors(n)[0], G.successors(n)[0],
                              weight=weight_new)
            G_simple.remove_node(n)
        if G_simple.out_degree(n) == 0 or G_simple.in_degree(0):
            G_simple.remove_node(n)
    return G_simple
