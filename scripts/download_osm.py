
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

nyc_rect = (-73.993498, 40.752273, -73.957058, 40.766382)
nyc_poly = [[-74.00851878077059, 40.75288995157469],
            [-74.01737732563862, 40.70363450274093],
            [-74.01243283598565, 40.69988947196632],
            [-73.99782710914521, 40.70743343850899],
            [-73.97742716598874, 40.71130380771929],
            [-73.97252636835454, 40.7284549818698],
            [-73.97378303735381, 40.73527282167493],
            [-73.97213846058494, 40.74251495015199],
            [-73.942645483123, 40.77548850560436],
            [-73.9454835793063, 40.78118853872636],
            [-73.94018677228019,40.78503171212724],
            [-73.93001170688356, 40.79925356887689],
            [-73.96094552328789, 40.81318684964225]]
# nyc_poly = [[-74.00754148198359, 40.75288922333515],
#             [-74.01252849969592, 40.70281168386228],
#             [-73.97972260096071, 40.71233020398169],
#             [-73.97403007816524, 40.71699082317848],
#             [-73.97380551930281, 40.73494149523898],
#             [-73.95261117871856, 40.76687333725763],
#             [-73.98634109096565, 40.78240568061087]]
nyc_speed = (25 * 1.61) / (60 * 60)  # km/sec


def all_pairs_times(G):
    print "Computing all pairs travel times..."
    dists = nx.floyd_warshall_numpy(G)
    return np.asarray(dists)


def all_pairs_paths(G):
    print "Computing all pairs paths..."
    paths = nx.all_pairs_dijkstra_path(G)
    return paths


def osm_graph(left, bottom, right, top):
    # print "Downloading OSM graph..."
    # osm_data = osm.download_osm(left, bottom, right, top)
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
    poly = planar.Polygon.from_points(nyc_poly)
    r = poly.bounding_box
    rect = (r.min_point.x, r.min_point.y, r.max_point.x, r.max_point.y)
    print rect
    G, stations, st_lookup = osm_graph(*rect)
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
        default="data/paths.csv",
        help="Output CSV file for the all pairs paths for the stations")
    args = parser.parse_args()
    write_graph(args.fn_graph, args.fn_paths)
