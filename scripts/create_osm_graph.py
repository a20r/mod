
import argparse
import planar
import networkx as nx
import numpy as np
import osm
import osm2nx
import pickle
import io
import csv
from progressbar import ProgressBar, ETA, Percentage, Bar


nyc_speed = (25 * 1.61) / (60 * 60)  # km/sec


def all_pairs_times(G):
    print "Computing all pairs travel distances..."
    dists = nx.floyd_warshall_numpy(G)
    return np.asarray(dists)


def all_pairs_paths(G):
    print "Computing all pairs paths..."
    paths = nx.johnson(G, weight="weight")
    return paths


def osm_graph(left, bottom, right, top):
    print "Making it a graph..."
    G = osm.read_osm("data/map.osm")
    print "Making it weighted..."
    G, max_distance = osm2nx.make_weighted(G)
    G = osm2nx.simplify_by_degree(G, max_distance)
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
                try:
                    path = paths[i][j]
                    id_path = list()
                    for n in path:
                        id_path.append(st_lookup[n])
                except KeyError:
                    id_path = [-1]
                start = st_lookup[i]
                end = st_lookup[j]
                writer.writerow([start, end] + id_path)
                pbar.update(counter + 1)
                counter += 1
        pbar.finish()


def write_graph(fn_graph, fn_paths):
    poly = planar.Polygon.from_points(common.nyc_poly)
    r = poly.bounding_box
    rect = (r.min_point.x, r.min_point.y, r.max_point.x, r.max_point.y)
    print "BBox:", rect
    G, stations, st_lookup = osm_graph(*rect)
    paths = all_pairs_paths(G)
    print "Writing paths to a file..."
    create_paths_file(G, st_lookup, paths, fn_paths)
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
    parser.add_argument(
        "--fn_paths", dest="fn_paths", type=str,
        default="data/paths.csv",
        help="Output CSV file for the all pairs paths for the stations")
    args = parser.parse_args()
    write_graph(args.fn_graph, args.fn_paths)
