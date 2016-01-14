
import io
import time
import csv
import numpy as np
import argparse
import sklearn.cluster as cluster
import pickle
import maps
import osm
import osm2nx
import networkx as nx
from geopy.distance import distance
from collections import OrderedDict, defaultdict
from progressbar import ProgressBar, ETA, Percentage, Bar


feature_names = ["p_time", "p_day", "passenger_count",
                 "p_station", "d_station"]

fn_stations_fields = ["id", "latitude", "longitude"]

fn_probs_fields = ["tau", "day", "pickup", "dropoff", "probability"]

fn_demands_fields = ["pickup_datetime", "pickup_station", "dropoff_datetime",
                     "dropoff_GPS_lon", "dropoff_GPS_lat", "dropoff_station",
                     "pickup_GPS_lon", "pickup_GPS_lat"]

fn_freqs_fields = ["time_interval", "expected_requests"]

date_format = "%Y-%m-%d %H:%M:%S"
date_format_tz = "%Y-%m-%d %H:%M:%S %Z"

nyc_rect = (-73.993498, 40.752273, -73.957058, 40.766382)


def percent_time(str_time):
    """
    Given a string representation of a date, this returns the percent of the
    day that the time is (i.e. 0.5 would be 12 noon)
    """
    t = time.strptime(str_time, date_format)
    secs = t.tm_hour * 60 * 60 + t.tm_min * 60 + t.tm_sec
    return secs / (24 * 60 * 60.0), t.tm_wday


def epoch_seconds(str_time):
    return int(time.mktime(time.strptime(str_time, date_format)))


def load_graph(fn_graph):
    with open(fn_graph, "r") as fin:
        fstr = fin.read()
        G_tuple = pickle.loads(fstr)
        return G_tuple


def closest_station(p, stations):
    dist = None
    m_station = None
    for i, st in enumerate(stations):
        p_dist = distance(p, st).kilometers
        if dist is None or p_dist < dist:
            dist = p_dist
            m_station = i
    return m_station


def file_length(fn_in):
    with open(fn_in, "rb") as fin:
        reader = csv.reader(fin)
        fl = sum(1 for _ in reader) - 1
        fin.seek(0)
        return fl


def is_within_box(plon, plat, dlon, dlat):
    plat = float(plat)
    plon = float(plon)
    dlat = float(dlat)
    dlon = float(dlon)
    pin_lat = plat > nyc_rect[1] and plat < nyc_rect[3]
    pin_lon = plon < nyc_rect[2] and plon > nyc_rect[0]
    din_lat = dlat > nyc_rect[1] and dlat < nyc_rect[3]
    din_lon = dlon < nyc_rect[2] and dlon > nyc_rect[0]
    return pin_lat and pin_lon and din_lat and din_lon


def clean_file(fn_raw, fn_cleaned):
    medals = set()
    taxi_count = 0
    with io.open(fn_raw, "rb") as fin:
        with io.open(fn_cleaned, "wb") as fout:
            reader = csv.reader(fin)
            writer = csv.writer(fout)
            fl = sum(1 for _ in reader) - 1
            fin.seek(0)
            pbar = ProgressBar(
                widgets=["Cleaning File: ", Bar(), Percentage(), "|", ETA()],
                maxval=fl + 1).start()
            for i, row in enumerate(reader):
                if i == 0:
                    writer.writerow(row)
                else:
                    try:
                        if not row[0] in medals:
                            taxi_count += 1
                            medals.add(row[0])
                        if is_within_box(row[10], row[11], row[12], row[13]):
                            writer.writerow(row)
                    except ValueError:
                        pass
                    pbar.update(i + 1)
            pbar.finish()
    return taxi_count


def clean_dict(val_dict):
    clean = dict()
    for key in val_dict.keys():
        k = key.strip()
        try:
            clean[k] = float(val_dict[key])
        except:
            clean[k] = val_dict[key]
    return clean


def find_stations(fn_in, **kwargs):
    """
    Uses k-means clustering to determine the taxi stations using the drop-off
    and pick-up locations
    """
    with io.open(fn_in, "rb") as fin:
        reader = csv.reader(fin)
        fl = sum(1 for _ in reader) - 1
        fin.seek(0)
        kmeans = cluster.MiniBatchKMeans(**kwargs)
        points = np.zeros((2 * fl, 2))
        pbar = ProgressBar(
            widgets=["Loading Locations: ", Bar(), Percentage(), "|", ETA()],
            maxval=fl + 1).start()
        for i, row in enumerate(reader):
            if i == 0:
                continue
            try:
                pts = np.zeros((2, 2))
                pts[0][0] = float(row[10])
                pts[0][1] = float(row[11])
                pts[1][0] = float(row[12])
                pts[1][1] = float(row[13])
                points[i - 1] = pts[0]
                points[i - 1 + fl] = pts[1]
            except:
                pass
            pbar.update(i + 1)
        pbar.finish()
        print "Finding Stations (This may take a while)..."
        kmeans.fit(points)
        return kmeans, fl


def extract_frequencies(fn_raw, stations, fl):
    num_pd = OrderedDict()
    num_ti = OrderedDict()
    num_tau = defaultdict(int)
    num_tau_occ = defaultdict(set)
    counter = 0
    pbar = ProgressBar(
        widgets=["Extracting Frequencies: ", Bar(), Percentage(), "|", ETA()],
        maxval=fl + 1).start()
    with io.open(fn_raw, "rb") as fin:
        reader = csv.DictReader(fin)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            try:
                row = clean_dict(row)
                p_time, p_day = percent_time(row["pickup_datetime"])
                p_l = [row["pickup_longitude"], row["pickup_latitude"]]
                d_l = [row["dropoff_longitude"], row["dropoff_latitude"]]
                sts = np.array([closest_station(p_l, stations),
                                closest_station(d_l, stations)])
                tau = int(4 * 24 * p_time)
                ti = (tau, p_day)
                if not ti in num_pd.keys():
                    num_pd[ti] = dict()
                if not ti in num_ti:
                    num_ti[ti] = 0
                if not (sts[0], sts[1]) in num_pd[ti]:
                    num_pd[ti][(sts[0], sts[1])] = 0
                    counter += 1
                num_pd[ti][(sts[0], sts[1])] += row["passenger_count"]
                num_ti[ti] += row["passenger_count"]
                num_tau[tau] += row["passenger_count"]
                num_tau_occ[tau].add(p_day)
            except ValueError:
                pass
            pbar.update(i + 1)
        pbar.finish()
    return num_pd, num_ti, num_tau, num_tau_occ, counter


def create_stations_file(fn_raw, fn_stations, stations):
    fn_javier = fn_stations.split(".")[0] + "_LUT.csv"
    pbar = ProgressBar(
        widgets=["Creating Stations File: ", Bar(), Percentage(), "|", ETA()],
        maxval=stations.shape[0]).start()
    with io.open(fn_stations, "wb") as fout:
        with io.open(fn_javier, "wb") as javier:
            javier_writer = csv.writer(javier, delimiter=" ")
            javier_writer.writerow([len(stations)])
            writer = csv.writer(fout)
            writer.writerow(fn_stations_fields)
            for i, center in enumerate(stations):
                row = list()
                row.append(i)
                row.append(center[0])
                row.append(center[1])
                writer.writerow(row)
                jrow = list()
                jrow.append(center[0])
                jrow.append(center[1])
                jrow.append(i)
                javier_writer.writerow(jrow)
                pbar.update(i + 1)
            pbar.finish()


def create_probs_file(fn_raw, fn_probs, fn_freqs, stations, fl):
    num_pd, num_ti, num_tau, num_tau_occ, counter = extract_frequencies(
        fn_raw, stations, fl)
    pbar = ProgressBar(
        widgets=["Creating Probabilities File: ", Bar(), Percentage(), "|",
                 ETA()],
        maxval=counter).start()
    with io.open(fn_probs, "wb") as fout:
        with io.open(fn_freqs, "wb") as fout_freqs:
            writer = csv.writer(fout)
            writer.writerow(fn_probs_fields)
            freqs_writer = csv.writer(fout_freqs)
            freqs_writer.writerow(fn_freqs_fields)
            seen = set()
            i = 0
            for (t, day) in num_pd.keys():
                for (p, d) in num_pd[(t, day)].keys():
                    ti = (t, day)
                    prob = num_pd[ti][(p, d)] / num_ti[ti]
                    writer.writerow([t, day, p, d, prob])
                    exp_reqs = num_tau[t] / float(len(num_tau_occ[t]))
                    if not t in seen:
                        freqs_writer.writerow([t, exp_reqs])
                        seen.add(t)
                    pbar.update(i + 1)
                    i += 1
            pbar.finish()


def create_times_file(stations, times, fn_times):
    pbar = ProgressBar(
        widgets=["Creating Times File: ", Bar(), Percentage(), "|", ETA()],
        maxval=stations.shape[0]).start()
    with io.open(fn_times, "wb") as fout:
        writer = csv.writer(fout, delimiter=" ")
        writer.writerow([stations.shape[0]])
        for i, row in enumerate(times):
            writer.writerow(row)
            pbar.update(i + 1)
        pbar.finish()


def create_demands_file(stations, fn_raw, fn_demands, fl):
    with io.open(fn_raw, "rb") as fin:
        with io.open(fn_demands, "wb") as fout:
            reader = csv.DictReader(fin)
            writer = csv.writer(fout, delimiter=' ')
            writer.writerow(fn_demands_fields)
            writer.writerow([fl - 1])
            pbar = ProgressBar(
                widgets=["Creating Demands File: ", Bar(),
                         Percentage(), "|", ETA()],
                maxval=fl + 1).start()
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                nrow = [None] * len(fn_demands_fields)
                row = clean_dict(row)
                p_l = [row["pickup_longitude"], row["pickup_latitude"]]
                d_l = [row["dropoff_longitude"], row["dropoff_latitude"]]
                locs = np.array([p_l, d_l])
                sts = np.array([closest_station(p_l, stations),
                                closest_station(d_l, stations)])
                nrow[0] = epoch_seconds(row["pickup_datetime"])
                nrow[1] = sts[0]
                nrow[2] = epoch_seconds(row["dropoff_datetime"])
                nrow[3] = row["dropoff_longitude"]
                nrow[4] = row["dropoff_latitude"]
                nrow[5] = sts[1]
                nrow[6] = row["pickup_longitude"]
                nrow[7] = row["pickup_latitude"]
                writer.writerow(nrow)
                pbar.update(i)
            pbar.finish()


def create_data_files_kmeans(fn_raw, fn_stations, fn_probs, fn_times,
                             fn_demands, fn_freqs, **kwargs):
    fn_cleaned = fn_raw.split(".")[0] + "_cleaned.csv"
    taxi_count = clean_file(fn_raw, fn_cleaned)
    kmeans, fl = find_stations(fn_cleaned, **kwargs)
    stations = kmeans.cluster_centers_
    times = maps.travel_times(stations)
    create_stations_file(fn_cleaned, fn_stations, stations)
    create_probs_file(fn_cleaned, fn_probs, fn_freqs, stations, fl)
    create_times_file(stations, times, fn_times)
    create_demands_file(stations, fn_cleaned, fn_demands, fl)
    print "Taxi Count:", taxi_count
    print "Done :D"


def create_data_files(fn_raw, fn_graph, fn_stations, fn_probs, fn_times,
                      fn_demands, fn_freqs):
    fn_cleaned = fn_raw.split(".")[0] + "_cleaned.csv"
    taxi_count = clean_file(fn_raw, fn_cleaned)
    print "Loading graph from file..."
    G, stations, st_lookup, times = load_graph(fn_graph)
    print "Determining file length..."
    fl = file_length(fn_cleaned)
    create_stations_file(fn_cleaned, fn_stations, stations)
    create_probs_file(fn_cleaned, fn_probs, fn_freqs, stations, fl)
    create_times_file(stations, times, fn_times)
    create_demands_file(stations, fn_cleaned, fn_demands, fl)
    print "Taxi Count:", taxi_count
    print "Done :D"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates feature files for taxi demand prediction.\
        It creates a file containing the geo-location of the stations and\
        a file containing the probability of a given origin, destination,\
        for a given time interval.")
    parser.add_argument(
        "--n_stations", dest="n_stations", type=int, default=101,
        help="Number of stations discovered using MiniBatchKMeans.")
    parser.add_argument(
        "--fn_raw", dest="fn_raw", type=str,
        default="data/trip_data_5_short.csv",
        help="CSV file containing the raw NY taxi data.")
    parser.add_argument(
        "--fn_graph", dest="fn_graph", type=str,
        default="data/manhattan_graph.pickle",
        help="Input pickle file for OSM graph data")
    parser.add_argument(
        "--fn_stations", dest="fn_stations", type=str,
        default="data/trip_data_5_stations_short.csv",
        help="Output CSV file for listing the stations.")
    parser.add_argument(
        "--fn_probs", dest="fn_probs", type=str,
        default="data/trip_data_5_probs_short.csv",
        help="Output CSV file for listing the demand probabilities.")
    parser.add_argument(
        "--fn_times", dest="fn_times", type=str,
        default="data/trip_data_5_times_short.csv",
        help="Output CSV file for listing the travel times between stations")
    parser.add_argument(
        "--fn_demands", dest="fn_demands", type=str,
        default="data/trip_data_5_demands_short.csv",
        help="Output CSV file for time series demands data")
    parser.add_argument(
        "--fn_freqs", dest="fn_freqs", type=str,
        default="data/trip_data_5_freqs_short.csv",
        help="Output CSV file for frequency of requests for different time\
        intervals over multiple days")
    args = parser.parse_args()
    create_data_files(args.fn_raw, args.fn_graph, args.fn_stations,
                      args.fn_probs, args.fn_times, args.fn_demands,
                      args.fn_freqs)
