
import io
import os.path
import numpy as np
import matplotlib.pyplot as plt
import pandas
import re
import seaborn as sns
from collections import defaultdict

__all__ = ["sns"]


TIME_STEP = 30
GRAPHS_PREFIX = "graphs"
DATA_FILE_TEMPLATE = "data-{}-{}.txt"
REG = r"[-+]?\d*\.\d+|\d+"


class PassengerData(object):
    def __init__(self, line):
        attrs = map(float, line)
        self.identity = attrs[0]
        self.origin = [attrs[2], attrs[1]]
        self.destination = [attrs[4], attrs[3]]
        self.station_origin = attrs[5]
        self.station_origin_coord = [attrs[7], attrs[6]]
        self.station_destination = attrs[8]
        self.station_destination_coord = [attrs[10], attrs[9]]
        self.time_req = attrs[11]
        self.time_pickup = attrs[12]
        self.time_dropoff = attrs[13]
        self.travel_time_optim = attrs[14]
        self.vehicle_pickup = attrs[15]


class PerformanceData(object):
    def __init__(self, line):
        attrs = map(float, line)
        self.n_pickups = attrs[0]
        self.total_pickups = attrs[1]
        self.n_dropoffs = attrs[2]
        self.total_dropoffs = attrs[3]
        self.n_ignored = attrs[4]
        self.total_ignored = attrs[5]


def extract_metrics(folder):
    g_folder = folder + GRAPHS_PREFIX + "/"
    data = defaultdict(list)
    t = 0
    while True:
        filename = g_folder + DATA_FILE_TEMPLATE.format(GRAPHS_PREFIX, t)
        print filename
        if not os.path.isfile(filename):
            return pandas.DataFrame(data)
        with io.open(filename) as fin:
            while True:
                line = fin.readline()
                if "Passengers" in line:
                    break
            line = re.findall(REG, fin.readline())
            if len(line) > 0:
                waiting_time = list()
                delay = list()
                while len(line) > 0:
                    pd = PassengerData(line)
                    waiting_time.append(pd.time_pickup - pd.time_req)
                    if pd.time_dropoff > 0:
                        delay.append(pd.time_dropoff - pd.time_req
                                     - pd.travel_time_optim)
                    line = re.findall(REG, fin.readline())
                data["mean_waiting_time"].append(np.mean(waiting_time))
                data["med_waiting_time"].append(np.median(waiting_time))
                data["mean_delay"].append(np.mean(delay))
                data["med_delay"].append(np.median(delay))
            else:
                data["mean_waiting_time"].append(0)
                data["med_waiting_time"].append(0)
                data["mean_delay"].append(0)
                data["med_delay"].append(0)

            fin.readline()
            line = re.findall(REG, fin.readline())
            pd = PerformanceData(line)
            data["time"].append(t)
            data["n_pickups"].append(pd.n_pickups)
            data["n_dropoffs"].append(pd.n_dropoffs)
            data["n_ignored"].append(pd.n_ignored)
        t += TIME_STEP


if __name__ == "__main__":
    sns.set_context("poster")
    data = extract_metrics("data/sim-data/")
    ma = pandas.rolling_mean(data["n_ignored"], 60)
    mstd = pandas.rolling_std(data["n_ignored"], 60)
    plt.plot(data["time"], data["n_ignored"], "b", alpha=0.2,
             label="Raw")
    plt.plot(data["time"], ma, "r", label="Moving Average")
    plt.fill_between(data["time"], ma - mstd, ma + mstd, color="r", alpha=0.4,
                     label="Standard Deviation")
    plt.xlabel("Time [s]")
    plt.ylabel("Number of Ignored Requests [s]")
    plt.legend()
    plt.show()
