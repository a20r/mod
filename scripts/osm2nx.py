
import common
import networkx as nx
import planar
import geopy as geo
from geopy.distance import distance

"""
This code has graciously been provided by the most honourable Aleksejs Sazonovs
"""


def make_weighted(G):
    max_distance = 0
    G = max(nx.strongly_connected_component_subgraphs(G), key=len)
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
    poly = planar.Polygon.from_points(common.nyc_poly)
    for n in G_simple.nodes():
        dead_node = G_simple.out_degree(n) == 0 or G_simple.in_degree(n) == 0
        vec = planar.Vec2(G.node[n]["data"].lon, G.node[n]["data"].lat)
        if not poly.contains_point(vec):
            G_simple.remove_node(n)
        elif G_simple.in_degree(n) == 1 and G_simple.out_degree(n) == 1:
            weight_in_n = G[G.predecessors(n)[0]][n]['weight']
            weight_out_n = G[n][G.successors(n)[0]]['weight']
            weight_new = weight_in_n + weight_out_n
            G_simple.add_edge(
                G.predecessors(n)[0], G.successors(n)[0], weight=weight_new)
            G_simple.remove_node(n)
        elif G_simple.has_node(n) and dead_node:
            G_simple.remove_node(n)
    return G_simple
