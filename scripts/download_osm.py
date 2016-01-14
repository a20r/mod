
import argparse
import networkx as nx
import numpy as np
import osm
import osm2nx
import pickle
import io
import csv
from progressbar import ProgressBar, ETA, Percentage, Bar

nyc_rect = (-73.993498, 40.752273, -73.957058, 40.766382)
nyc_speed = (25 * 1.61) / (60 * 60)  # km/sec


def all_pairs_times(G):
    print "Computing all pairs travel times..."
    dists = nx.floyd_warshall_numpy(G)
    return np.asarray(dists / nyc_speed)


def all_pairs_paths(G):
    print "Computing all pairs paths..."
    paths = nx.all_pairs_dijkstra_path(G)
    return paths


def osm_graph(left, bottom, right, top):
    print "Downloading OSM graph..."
    osm_data = osm.download_osm(left, bottom, right, top)
    print "Making it a graph..."
    G = osm.read_osm(osm_data)
    print "Making it weighted..."
    G, max_distance = osm2nx.make_weighted(G)
    print "Number of nodes:", len(G.nodes())
    stations = np.zeros((len(G.nodes()), 2))
    st_lookup = dict()
    print "Determining stations..."
    for i, n in enumerate(G.nodes()):
        stations[i][0] = G.node[n]["data"].lon
        stations[i][1] = G.node[n]["data"].lat
        st_lookup[n] = i
    return G, stations, st_lookup


def create_paths_file(G, st_lookup, paths, fn_paths):
    counter = 0
    pbar = ProgressBar(
        widgets=["Creating Paths File: ", Bar(), Percentage(), "|", ETA()],
        maxval=pow(len(G.nodes()), 2)).start()
    with io.open(fn_paths, "wb") as fout:
        writer = csv.writer(fout, delimiter=" ")
        for i in G.nodes():
            for j in G.nodes():
                path = paths[i][j]
                id_path = list()
                for n in path:
                    id_path.append(st_lookup[n])
                start = st_lookup[i]
                end = st_lookup[j]
                writer.writerow([start, end] + id_path)
                pbar.update(counter + 1)
                counter += 1
        pbar.finish()


def write_graph(fn_graph, fn_paths):
    G, stations, st_lookup = osm_graph(*nyc_rect)
    dists = all_pairs_times(G)
    paths = all_pairs_paths(G)
    G_tuple = (G, stations, st_lookup, dists)
    print "Writing graph data to file..."
    pstr = pickle.dumps(G_tuple)
    with open(fn_graph, "wb") as fout:
        fout.write(pstr)
    print "Writing paths to a file..."
    create_paths_file(G, st_lookup, paths, fn_paths)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Downloads and creates a graph from Manhattan OSM data")
    parser.add_argument(
        "--fn_graph", dest="fn_graph", type=str,
        default="data/manhattan_graph.pickle",
        help="Output file for the pickled graph data to be written")
    parser.add_argument(
        "--fn_paths", dest="fn_paths", type=str,
        default="data/trip_data_5_paths_short.csv",
        help="Output CSV file for the all pairs paths for the stations")
    args = parser.parse_args()
    write_graph(args.fn_graph, args.fn_paths)
