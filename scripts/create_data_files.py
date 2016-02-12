
import io
import common
import time
import csv
import numpy as np
import argparse
import pickle
import planar
import scipy.spatial as spatial
from collections import OrderedDict, defaultdict
from progressbar import ProgressBar, ETA, Percentage, Bar


fn_probs_fields = ["tau", "day", "pickup", "dropoff", "probability"]

fn_demands_fields = ["pickup_datetime", "pickup_station", "dropoff_datetime",
                     "dropoff_GPS_lon", "dropoff_GPS_lat", "dropoff_station",
                     "pickup_GPS_lon", "pickup_GPS_lat"]

fn_freqs_fields = ["time_interval", "expected_requests"]

day_dem_template = "data/demands_{}_{}_{}.csv"


def percent_time(str_time):
    """
    Given a string representation of a date, this returns the percent of the
    day that the time is (i.e. 0.5 would be 12 noon)
    """
    t = time.strptime(str_time, common.date_format)
    secs = t.tm_hour * 60 * 60 + t.tm_min * 60 + t.tm_sec
    return secs / (24 * 60 * 60.0), t.tm_wday


def epoch_seconds(str_time):
    return int(time.mktime(time.strptime(str_time, common.date_format)))


def load_graph(fn_graph):
    with open(fn_graph, "r") as fin:
        fstr = fin.read()
        G_tuple = pickle.loads(fstr)
        return G_tuple


def file_length(fn_in):
    with open(fn_in, "rb") as fin:
        reader = csv.reader(fin)
        fl = sum(1 for _ in reader) - 1
        fin.seek(0)
        return fl


def clean_file(fn_raw, fn_cleaned):
    medals = set()
    poly = planar.Polygon.from_points(common.nyc_poly)
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
                        c_p = poly.contains_point(planar.Vec2(
                            float(row[10]), float(row[11])))
                        c_d = poly.contains_point(planar.Vec2(
                            float(row[12]), float(row[13])))
                        if c_p and c_d:
                            writer.writerow(row)
                            medals.add(row[0])
                    except ValueError:
                        pass
                    pbar.update(i + 1)
            pbar.finish()
    return len(medals)


def extract_frequencies(fn_raw, stations, kd, fl):
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
                row = common.clean_dict(row)
                p_time, p_day = percent_time(row["pickup_datetime"])
                p_l = [row["pickup_longitude"], row["pickup_latitude"]]
                d_l = [row["dropoff_longitude"], row["dropoff_latitude"]]
                _, sts = kd.query(np.array([p_l, d_l]))
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


def create_stations_file(fn_stations, stations):
    fn_javier = fn_stations.split(".")[0] + "_LUT.csv"
    pbar = ProgressBar(
        widgets=["Creating Stations File: ", Bar(), Percentage(), "|", ETA()],
        maxval=stations.shape[0]).start()
    with io.open(fn_stations, "wb") as fout:
        with io.open(fn_javier, "wb") as javier:
            javier_writer = csv.writer(javier, delimiter=" ")
            javier_writer.writerow([len(stations)])
            writer = csv.writer(fout)
            writer.writerow(common.fn_stations_fields)
            for i, center in enumerate(stations):
                row = list()
                row.append(i)
                row.append(center[1])
                row.append(center[0])
                writer.writerow(row)
                jrow = list()
                jrow.append(center[0])
                jrow.append(center[1])
                jrow.append(i)
                javier_writer.writerow(jrow)
                pbar.update(i + 1)
            pbar.finish()


def create_probs_file(fn_raw, fn_probs, fn_freqs, stations, kd, fl):
    num_pd, num_ti, num_tau, num_tau_occ, counter = extract_frequencies(
        fn_raw, stations, kd, fl)
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


def create_demands_file(stations, fn_raw, fn_demands, kd, fl):
    pbar = ProgressBar(
        widgets=["Creating Demands File: ", Bar(),
                 Percentage(), "|", ETA()],
        maxval=fl + 1).start()
    cur_date = (0, 0, 0)
    fout = None
    writer = None
    counter = 0
    rows = list()
    with io.open(fn_raw, "rb") as fin:
        reader = csv.DictReader(fin)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            nrow = [None] * len(fn_demands_fields)
            row = common.clean_dict(row)
            str_time = row["pickup_datetime"]
            t = time.strptime(str_time, common.date_format)
            cdate = (t.tm_wday + 1, t.tm_yday // 7, t.tm_year)
            if cdate != cur_date:
                cur_date = cdate
                fname = day_dem_template.format(*cur_date)
                fout = io.open(fname, "wb")
                writer = csv.writer(fout, delimiter=" ")
                writer.writerow(fn_demands_fields)
                writer.writerow([counter])
                writer.writerows(rows)
                rows = list()
                fout.close()
                counter = 0
            p_l = [row["pickup_longitude"], row["pickup_latitude"]]
            d_l = [row["dropoff_longitude"], row["dropoff_latitude"]]
            _, sts = kd.query(np.array([p_l, d_l]))
            nrow[0] = epoch_seconds(row["pickup_datetime"])
            nrow[1] = sts[0]
            nrow[2] = epoch_seconds(row["dropoff_datetime"])
            nrow[3] = row["dropoff_longitude"]
            nrow[4] = row["dropoff_latitude"]
            nrow[5] = sts[1]
            nrow[6] = row["pickup_longitude"]
            nrow[7] = row["pickup_latitude"]
            rows.append(nrow)
            counter += 1
            pbar.update(i)
        pbar.finish()


def create_data_files(fn_raw, fn_graph, fn_stations, fn_probs,
                      fn_demands, fn_freqs):
    fn_cleaned = fn_raw.split(".")[0] + "_cleaned.csv"
    taxi_count = clean_file(fn_raw, fn_cleaned)
    print "Loading graph from file..."
    G, stations = load_graph(fn_graph)
    kd = spatial.KDTree(stations)
    print "Determining file length..."
    fl = file_length(fn_cleaned)
    create_stations_file(fn_stations, stations)
    create_demands_file(stations, fn_cleaned, fn_demands, kd, fl)
    create_probs_file(fn_cleaned, fn_probs, fn_freqs, stations, kd, fl)
    print "Taxi Count:", taxi_count
    print "Done :D"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates feature files for taxi demand prediction.\
        It creates a file containing the geo-location of the stations and\
        a file containing the probability of a given origin, destination,\
        for a given time interval.")
    parser.add_argument(
        "--fn_raw", dest="fn_raw", type=str,
        default="data/data_short.csv",
        help="CSV file containing the raw NY taxi data.")
    parser.add_argument(
        "--fn_graph", dest="fn_graph", type=str,
        default="data/manhattan_graph.pickle",
        help="Input pickle file for OSM graph data")
    parser.add_argument(
        "--fn_stations", dest="fn_stations", type=str,
        default="data/stations.csv",
        help="Output CSV file for listing the stations.")
    parser.add_argument(
        "--fn_probs", dest="fn_probs", type=str,
        default="data/probs.csv",
        help="Output CSV file for listing the demand probabilities.")
    parser.add_argument(
        "--fn_demands", dest="fn_demands", type=str,
        default="data/demands.csv",
        help="Output CSV file for time series demands data")
    parser.add_argument(
        "--fn_freqs", dest="fn_freqs", type=str,
        default="data/freqs.csv",
        help="Output CSV file for frequency of requests for different time\
        intervals over multiple days")
    args = parser.parse_args()
    create_data_files(args.fn_raw, args.fn_graph, args.fn_stations,
                      args.fn_probs, args.fn_demands, args.fn_freqs)
