
import io
import common
import os
import os.path
import numpy as np
import matplotlib.pyplot as plt
import pandas
import re
from collections import defaultdict
from datetime import datetime
from progressbar import ProgressBar, ETA, Percentage, Bar


TIME_STEP = 30
GRAPHS_PREFIX = "graphs"
DATA_FILE_TEMPLATE = "data-{}-{}.txt"
REG = r"-?\d*\.\d+|-?\d+"
START_DATE = "2013-05-03 19:00:00"


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


def process_vehicles(fin, data, n_vecs, cap, rebalancing, is_long):
    fin.readline()
    n_reqs = int(re.findall(r"\d+", fin.readline())[0])
    data["n_reqs"].append(n_reqs)
    while True:
        line = fin.readline()
        if "Vehicles" in line:
            break
    ppv = list()
    line = fin.readline()
    while len(line) > 1:
        passes = re.findall(r"-?\d+", line.split("%")[1])
        ppv.append(len(passes))
        line = fin.readline()
    data["mean_passengers"].append(np.mean(ppv))
    data["med_passengers"].append(np.median(ppv))
    data["std_passengers"].append(np.std(ppv))
    data["n_vehicles"].append(n_vecs)
    data["capacity"].append(cap)
    data["rebalancing"].append(rebalancing)
    data["is_long"].append(is_long)


def move_to_passengers(fin, data):
    while True:
        line = fin.readline()
        if "Passengers" in line:
            n_pass = int(re.findall(r"\d+", line)[0])
            data["total_passengers"].append(n_pass)
            return


def process_passengers(fin, data):
    l = fin.readline()
    line = re.findall(REG, l)
    if len(line) > 0:
        waiting_time = list()
        delay = list()
        debug = 0
        while len(line) > 0:
            pd = PassengerData(line)
            waiting_time.append(pd.time_pickup - pd.time_req)
            if pd.time_dropoff > 0:
                dly = pd.time_dropoff - pd.time_req - pd.travel_time_optim
                delay.append(dly)
            l = fin.readline()
            line = re.findall(REG, l)
        data["mean_waiting_time"].append(np.mean(waiting_time))
        data["med_waiting_time"].append(np.median(waiting_time))
        data["std_waiting_time"].append(np.std(waiting_time))
        data["mean_delay"].append(np.mean(delay))
        data["med_delay"].append(np.median(delay))
        data["std_delay"].append(np.std(delay))
    else:
        data["mean_waiting_time"].append(0)
        data["med_waiting_time"].append(0)
        data["std_waiting_time"].append(0)
        data["mean_delay"].append(0)
        data["med_delay"].append(0)
        data["std_delay"].append(0)


def process_performance(fin, data):
    fin.readline()
    line = re.findall(REG, fin.readline())
    pd = PerformanceData(line)
    data["n_pickups"].append(pd.n_pickups)
    data["n_dropoffs"].append(pd.n_dropoffs)
    data["n_ignored"].append(pd.n_ignored)


def convert_to_dataframe(data, is_long=0):
    freq = "30S"
    if is_long == 0:
        start = datetime.strptime(START_DATE, common.date_format)
        periods = common.MAX_SECONDS / 30
    else:
        start = datetime.strptime("2013-05-03 19:00:00", common.date_format)
        periods = len(data["is_long"])
    inds = pandas.date_range(start=start, periods=periods, freq=freq)
    for k in data.keys():
        data[k] = np.array(data[k])
    data["capacity"] = np.array(data["capacity"], dtype=int)
    data["n_vehicles"] = np.array(data["n_vehicles"], dtype=int)
    # data["time"] = inds
    return pandas.DataFrame(data)


def extract_metrics(folder, n_vecs, cap, rebalancing, is_long):
    g_folder = folder + GRAPHS_PREFIX + "/"
    data = defaultdict(list)
    if is_long == 0:
        fl = common.MAX_SECONDS / 30
    else:
        fl = len(os.listdir(g_folder))
    preface = "Extracting Metrics (" + g_folder + "): "
    widgets = [preface, Bar(), Percentage(), "| ", ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=fl).start()
    for i in xrange(fl):
        try:
            t = i * TIME_STEP
            filename = g_folder + DATA_FILE_TEMPLATE.format(GRAPHS_PREFIX, t)
            with io.open(filename) as fin:
                process_vehicles(fin, data, n_vecs, cap, rebalancing, is_long)
                move_to_passengers(fin, data)
                process_passengers(fin, data)
                process_performance(fin, data)
            pbar.update(i)
        except IOError:
            pass
    pbar.finish()
    return convert_to_dataframe(data, is_long)


def load_parameters(param_file):
    params = dict()
    with io.open(param_file, "rb") as fin:
        for line in fin:
            vs = line.split(":")
            key = vs[0]
            values = re.findall(REG, vs[1])
            if len(values) > 0:
                params[key] = float(values[0])
            else:
                params[key] = vs[1].strip()
        return params


def extract_dataframe(folder):
    dirs = os.listdir(folder)
    dfs = list()
    for dr in dirs:
        subdir = folder + dr + "/"
        params = load_parameters(subdir + "parameters.txt")
        n_vehicles = params["NUMBER_VEHICLES"]
        cap = params["maxPassengersVehicle"]
        rebalancing = params["USE_REBALANCING"]
        is_long = params.get("is_long", 0)
        df = extract_metrics(subdir, n_vehicles, cap, rebalancing, is_long)
        dfs.append(df)
    return pandas.concat(dfs)


if __name__ == "__main__":
    print "Extracting Metrics DataFrame..."
    df = extract_dataframe("data/sim-data/")
    print "Writing DataFrame to File..."
    df.to_csv("data/metrics.csv")
