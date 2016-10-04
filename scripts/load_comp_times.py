
import glob
import os.path as path
import pandas as pd
from itertools import product
from plot_metrics import print_here


NFS_PATH = "/home/wallar/nfs/data/data-sim/"
NFS_PATH = "/data/drl/mod_sim_data/data-sim/"


predictions = ["0-nR", 0, 100, 200, 300, 400]
waiting_times = [120, 300, 420]
vehicles = [1000, 2000, 3000]
caps = [1, 2, 4, 10]
intervals = [10, 20, 30, 40, 50]


@print_here()
def get_comp_filenames(vecs, cap, wt, preds, day):
    dir_temp = "v{0}-c{1}-w{2}-p{3}/v{0}-c{1}-w{2}-p{3}-{4}-18-2013-*/graphs/"
    graph_dir = dir_temp.format(vecs, cap, wt, preds, day)
    first = glob.glob(NFS_PATH + graph_dir + "data-graphs-0.txt")[0]
    last = glob.glob(NFS_PATH + graph_dir + "data-graphs-86340.txt")[0]
    return first, last


def get_interval_comp_filenames(interval, day):
    if interval == 30:
        return get_comp_filenames(2000, 4, 300, 0, day)
    dir_temp = ("v{0}-c{1}-w{2}-p{3}-i{5}/"
                "v{0}-c{1}-w{2}-p{3}-{4}-18-2013-*/graphs/")
    graph_dir = dir_temp.format(2000, 4, 300, 0, day, interval)
    total_secs = 24 * 60 * 60 - 60
    last_file_secs = interval * (total_secs / interval)
    last_file = "data-graphs-{}.txt".format(last_file_secs)
    first = glob.glob(NFS_PATH + graph_dir + "data-graphs-0.txt")[0]
    last = glob.glob(NFS_PATH + graph_dir + last_file)[0]
    return first, last


@print_here()
def generate_interval_time_df():
    cols = ["interval", "day", "comp_time"]
    data = pd.DataFrame(columns=cols)
    counter = 0
    for i, d in product(intervals, range(1, 8)):
        s, e = get_interval_comp_filenames(i, d)
        total_secs = (24 * 60 * 60) / i
        diff = (path.getctime(e) - path.getctime(s)) / total_secs
        if diff > 500:
            diff = 2.9
        data.loc[counter] = [i, d - 1, diff]
        counter += 1
    return data


@print_here()
def generate_time_df():
    cols = ["vehicles", "capacity", "waiting_time", "day", "comp_time"]
    data = pd.DataFrame(columns=cols)
    counter = 0
    for v, c, wt, d in product(vehicles, caps, waiting_times, range(1, 8)):
        s, e = get_comp_filenames(v, c, wt, 0, d)
        diff = (path.getctime(e) - path.getctime(s)) / 2878
        if diff > 500:
            diff = 2.9
        data.loc[counter] = [v, c, wt, d - 1, diff]
        counter += 1
    return data


if __name__ == "__main__":
    df = generate_interval_time_df()
    print df
    df.to_csv("data/interval-times.csv")
