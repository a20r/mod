
import argparse
import networkx as nx
import numpy as np
import osm
import osm2nx
import pickle


nyc_rect = (-73.985076, 40.753528, -73.952211, 40.772996)
nyc_speed = (25 * 1.61) / (60 * 60)  # km/sec


def all_pairs_times(G):
    print "Computing all pairs travel times..."
    dists = nx.floyd_warshall_numpy(G)
    return np.asarray(dists / nyc_speed)


def osm_graph(left, bottom, right, top):
    print "Downloading OSM graph..."
    osm_data = osm.download_osm(left, bottom, right, top)
    print "Making it a graph..."
    G = osm.read_osm(osm_data)
    print "Making it weighted..."
    G, max_distance = osm2nx.make_weighted(G)
    stations = np.zeros((len(G.nodes()), 2))
    st_lookup = dict()
    print "Determining stations..."
    for i, n in enumerate(G.nodes()):
        stations[i][0] = G.node[n]["data"].lon
        stations[i][1] = G.node[n]["data"].lat
        st_lookup[n] = i
    return G, stations, st_lookup


def write_graph(fn_graph):
    G, stations, st_lookup = osm_graph(*nyc_rect)
    dists = all_pairs_times(G)
    G_tuple = (G, stations, st_lookup, dists)
    print "Writing graph data to file..."
    pstr = pickle.dumps(G_tuple)
    with open(fn_graph, "wb") as fout:
        fout.write(pstr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Downloads and creates a graph from Manhattan OSM data")
    parser.add_argument(
        "--fn_graph", dest="fn_graph", type=str,
        default="data/manhattan_graph.pickle",
        help="Output file for the pickled graph data to be written")
    args = parser.parse_args()
    write_graph(args.fn_graph)
