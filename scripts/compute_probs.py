
import pandas as pd
import numpy as np
import tqdm
import common
import argparse
from scipy.spatial import KDTree
from multiprocessing import Pool


parser = argparse.ArgumentParser(
    description="Computes a frequency distribution for taxi trips")
parser.add_argument(
    "--fn_cleaned", dest="fn_cleaned", type=str,
    default="data/trip_data_short_cleaned.csv",
    help="Cleaned data used to calculate frequencies")
parser.add_argument(
    "--fn_stations", dest="fn_stations", type=str,
    default="data/stations-mod.csv",
    help="Should be the stations found from the points.csv")
parser.add_argument(
    "--fn_freqs", dest="fn_freqs", type=str,
    default="data/freqs.npy",
    help="Output filename for the frequency table")
args = parser.parse_args()

stations = pd.read_csv(args.fn_stations)
stations_kd = KDTree(stations.as_matrix(["lng", "lat"]))
sts = stations.as_matrix(["lng", "lat"])
n_stations = stations.shape[0]
interval_length = 15
mins_per_day = 24 * 60
intervals_per_day = mins_per_day / interval_length
n_lines = 165114362


def calc_freqs(df):
    np.seterr(all='ignore')
    freqs = np.zeros((intervals_per_day, 7, n_stations, n_stations),
                     dtype=np.int)
    df = common.clean_df(df)
    for i, row in df.iterrows():
        p_dt = row["pickup_datetime"]
        interval, wday = common.convert_date_to_interval(
            p_dt, interval_length)
        pickup = np.array([row["pickup_longitude"],
                           row["pickup_latitude"]])
        dropoff = np.array([row["dropoff_longitude"],
                            row["dropoff_latitude"]])
        _, p_label = stations_kd.query(pickup)
        _, d_label = stations_kd.query(dropoff)
        freqs[interval][wday][p_label][d_label] += 1
    del df
    return freqs


if __name__ == "__main__":
    n_workers = 4
    chunksize = 10000
    pool = Pool(n_workers, maxtasksperchild=1)
    dfs = common.load_data(args.fn_cleaned, chunksize)
    freqs = np.zeros((intervals_per_day, 7, n_stations, n_stations),
                     dtype=np.int)
    stuff_to_do = True
    pbar = tqdm.tqdm(desc="Computing probabilities")
    while stuff_to_do:
        sub_dfs = list()
        for i in xrange(n_workers):
            try:
                sub_dfs.append(next(dfs))
            except StopIteration:
                stuff_to_do = False
            except ValueError:
                stuff_to_do = False
        if len(sub_dfs) > 0:
            freqs += sum(pool.map(calc_freqs, sub_dfs))
            updated = sum(df.shape[0] for df in sub_dfs)
            pbar.update(updated)
            for df in sub_dfs:
                del df
    pbar.close()
    pool.close()
    np.save(args.fn_freqs, freqs)
