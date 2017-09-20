
import sklearn.neighbors as nn
import numpy as np
import pandas as pd
import argparse


def find_clusters(geos, tol):
    hav_tol = tol / 6371.0
    used = [False] * len(geos)
    ball_tree = nn.BallTree(np.radians(geos), metric="haversine")
    centers = list()
    for i in xrange(len(geos)):
        if not used[i]:
            loc = geos[i]
            st = np.array([i, loc[0], loc[1]])
            centers.append(st)
            nearest = ball_tree.query_radius([np.radians(loc)], hav_tol)[0]
            for i in nearest:
                used[i] = True
    return np.array(centers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Greedily find stations with a ball tree")
    parser.add_argument(
        "--fn_nodes", dest="fn_nodes", type=str,
        default="data/nyc-graph/points.csv",
        help="Should be the points used for the graph")
    parser.add_argument(
        "--dist", dest="dist", type=float,
        default=0.45,
        help="Distance between centers in Km (I think)")
    parser.add_argument(
        "--fn_stations", dest="fn_stations", type=str,
        default="data/stations-mod.csv",
        help="Output CSV file for listing the stations")
    args = parser.parse_args()

    nyc_nodes = pd.read_csv(args.fn_nodes,
                            names=["id", "lat", "lon"])
    nyc_mat = nyc_nodes.as_matrix(["lon", "lat"])
    stations = find_clusters(nyc_mat, args.dist)
    np.savetxt(args.fn_stations, stations, delimiter=",",
               header="id,lng,lat", fmt=["%d", "%.18f", "%.18f"], comments="")
    print "Stations:", len(stations)
