
import common
import argparse
import planar
import networkx as nx
import numpy as np
import pickle
import io
import csv
from geopy.distance import distance
import geopy as geo
from progressbar import ProgressBar, ETA, Percentage, Bar


def load_graph(nyc_dir):
    print "Making it a graph..."
    sts = np.loadtxt(nyc_dir + "points.csv", delimiter=",")
    edges = np.loadtxt(nyc_dir + "edges.csv", delimiter=",")
    times = np.loadtxt(nyc_dir + "week.csv", delimiter=",")
    G = nx.DiGraph()
    for i in xrange(sts.shape[0]):
        G.add_node(i, lat=sts[i][1], lon=sts[i][2])
    for i in xrange(edges.shape[0]):
        t = np.mean(times[i][1:])
        std = np.std(times[i][1:])
        G.add_edge(edges[i][1] - 1, edges[i][2] - 1, weight=t, std=std)
    return G, np.fliplr(sts[:, 1:])


def path_length(G, path):
    length = 0.0
    for i in xrange(len(path) - 1):
        sdata = G.node[path[i]]
        edata = G.node[path[i + 1]]
        src = geo.Point(sdata["lat"], sdata["lon"])
        end = geo.Point(edata["lat"], edata["lon"])
        length += distance(src, end).kilometers
    return length


def create_paths_file(G, fn_paths, fn_times):
    counter = 0
    pbar = ProgressBar(
        widgets=["Creating Paths File: ", Bar(), Percentage(), "|", ETA()],
        maxval=pow(len(G.nodes()), 2)).start()
    with io.open(fn_paths, "wb") as fout:
        with io.open(fn_times, "wb") as ftimes:
            writer = csv.writer(fout, delimiter=" ")
            times_writer = csv.writer(ftimes, delimiter=" ")
            times_writer.writerow([len(G.nodes())])
            for i in G.nodes():
                tts, paths = nx.single_source_dijkstra(G, i)
                rows = list()
                time_row = [-1] * len(G.nodes())
                for j in paths.keys():
                    time_row[int(j)] = "%.1f" % tts[int(j)]
                    rows.append([i, j] + map(int, paths[j]))
                    pbar.update(counter + 1)
                    counter += 1
                writer.writerows(rows)
                times_writer.writerow(time_row)
            pbar.finish()


def write_graph(fn_graph, fn_paths, fn_times, nyc_dir):
    poly = planar.Polygon.from_points(common.nyc_poly)
    r = poly.bounding_box
    rect = (r.min_point.x, r.min_point.y, r.max_point.x, r.max_point.y)
    print "BBox:", rect
    G, stations = load_graph(nyc_dir)
    create_paths_file(G, fn_paths, fn_times)
    G_tuple = (G, stations)
    print "Writing graph data to file..."
    pstr = pickle.dumps(G_tuple)
    with open(fn_graph, "wb") as fout:
        fout.write(pstr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates a graph based on Carlo's data")
    parser.add_argument(
        "--nyc_dir", dest="nyc_dir", type=str,
        default="data/nyc/",
        help="Directory for the NYC graph data")
    parser.add_argument(
        "--fn_graph", dest="fn_graph", type=str,
        default="data/manhattan_graph.pickle",
        help="Output file for the pickled graph data to be written")
    parser.add_argument(
        "--fn_paths", dest="fn_paths", type=str,
        default="data/paths.csv",
        help="Output CSV file for the all pairs paths for the stations")
    parser.add_argument(
        "--fn_times", dest="fn_times", type=str,
        default="data/times.csv",
        help="Output CSV file for listing the travel times between stations")
    args = parser.parse_args()
    write_graph(args.fn_graph, args.fn_paths, args.fn_times, args.nyc_dir)
