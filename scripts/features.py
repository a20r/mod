
import io
import time
import csv
import numpy as np
import argparse
import sklearn.cluster as cluster
import maps
from collections import defaultdict, OrderedDict
from progressbar import ProgressBar, ETA, Percentage, Bar


feature_names = ["p_time", "p_day", "passenger_count",
                 "p_station", "d_station"]

fn_stations_fields = ["id", "latitude", "longitude"]

fn_probs_fields = ["tau", "day", "pickup", "dropoff", "probability"]

fn_demands_fields = ["pickup_datetime", "pickup_station", "dropoff_datetime",
                     "dropoff_GPS_lon", "dropoff_GPS_lat", "dropoff_station",
                     "pickup_GPS_lon", "pickup_GPS_lat"]

date_format = "%Y-%m-%d %H:%M:%S"


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


def clean_file(fn_raw, fn_cleaned):
    with io.open(fn_raw, "rb") as fin:
        with io.open(fn_cleaned, "wb") as fout:
            reader = csv.reader(fin)
            writer = csv.writer(fout)
            for i, row in enumerate(reader):
                if i == 0:
                    writer.writerow(row)
                else:
                    p_lat_zero = int(float(row[10])) == 0
                    p_lon_zero = int(float(row[11])) == 0
                    d_lat_zero = int(float(row[12])) == 0
                    d_lon_zero = int(float(row[13])) == 0
                    p_zero = p_lat_zero and p_lon_zero
                    d_zero = d_lat_zero and d_lon_zero
                    if not (p_zero and d_zero):
                        writer.writerow(row)


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
        kmeans.fit(points)
        return kmeans


def extract_frequencies(fn_raw, kmeans):
    num_pd = OrderedDict()
    num_ti = OrderedDict()
    with io.open(fn_raw, "rb") as fin:
        reader = csv.DictReader(fin)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            try:
                row = clean_dict(row)
                p_time, p_day = percent_time(row["pickup_datetime"])
                p_l = [row["pickup_longitude"], row["pickup_latitude"]]
                d_l = [row["dropoff_longitude"], row["dropoff_longitude"]]
                locs = np.array([p_l, d_l])
                sts = kmeans.predict(locs)
                tau = int(4 * 24 * p_time)
                ti = (tau, p_day)

                if not ti in num_pd.keys():
                    num_pd[ti] = defaultdict(float)
                if not ti in num_ti:
                    num_ti[ti] = 0.0

                num_pd[ti][(sts[0], sts[1])] += row["passenger_count"]
                num_ti[ti] += row["passenger_count"]
            except ValueError:
                pass
    return num_pd, num_ti


def create_stations_file(fn_raw, fn_stations, **kwargs):
    kmeans = find_stations(fn_raw, **kwargs)
    with io.open(fn_stations, "wb") as fout:
        writer = csv.writer(fout)
        writer.writerow(fn_stations_fields)
        for i, center in enumerate(kmeans.cluster_centers_):
            row = list()
            row.append(i)
            row.append(center[1])
            row.append(center[0])
            writer.writerow(row)
    return kmeans


def create_probs_file(fn_raw, fn_probs, kmeans):
    num_pd, num_ti = extract_frequencies(fn_raw, kmeans)
    with io.open(fn_probs, "wb") as fout:
        writer = csv.writer(fout)
        writer.writerow(fn_probs_fields)
        for (t, day) in num_pd.keys():
            for (p, d) in num_pd[(t, day)].keys():
                ti = (t, day)
                prob = num_pd[ti][(p, d)] / num_ti[ti]
                writer.writerow([t, day, p, d, prob])


def create_times_file(kmeans, fn_times):
    times = maps.travel_times(kmeans.cluster_centers_, 0)
    with io.open(fn_times, "wb") as fout:
        writer = csv.writer(fout, delimiter=" ")
        for row in times:
            writer.writerow(row)


def create_demands_file(kmeans, fn_raw, fn_demands):
    with io.open(fn_raw, "rb") as fin:
        with io.open(fn_demands, "wb") as fout:
            reader = csv.DictReader(fin)
            fl = sum(1 for _ in reader) - 1
            fin.seek(0)
            writer = csv.writer(fout, delimiter=' ')
            writer.writerow(fn_demands_fields)
            writer.writerow([fl])
            pbar = ProgressBar(widgets=[Percentage(), ETA(), Bar()],
                               maxval=300).start()
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                nrow = [None] * len(fn_demands_fields)
                row = clean_dict(row)
                p_l = [row["pickup_longitude"], row["pickup_latitude"]]
                d_l = [row["dropoff_longitude"], row["dropoff_longitude"]]
                locs = np.array([p_l, d_l])
                sts = kmeans.predict(locs)
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


def create_feature_files(fn_raw, fn_stations, fn_probs, fn_times,
                         fn_demands, **kwargs):
    print "Cleaning input file..."
    fn_cleaned = fn_raw.split(".")[0] + "_cleaned.csv"
    clean_file(fn_raw, fn_cleaned)
    print "Creating stations file..."
    kmeans = create_stations_file(fn_cleaned, fn_stations, **kwargs)
    print "Creating probability file..."
    create_probs_file(fn_cleaned, fn_probs, kmeans)
    print "Creating travel times file..."
    create_times_file(kmeans, fn_times)
    print "Creating demands file..."
    create_demands_file(kmeans, fn_cleaned, fn_demands)
    print "Done :D"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates feature files for taxi demand prediction.\
        It creates a file containing the geo-location of the stations and\
        a file containing the probability of a given origin, destination,\
        for a given time interval.")
    parser.add_argument(
        "--n_stations", dest="n_stations", type=int, default=10,
        help="Number of stations discovered using MiniBatchKMeans.")
    parser.add_argument(
        "--fn_raw", dest="fn_raw", type=str,
        default="data/trip_data_5_short.csv",
        help="CSV file containing the raw NY taxi data.")
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
    args = parser.parse_args()
    create_feature_files(args.fn_raw, args.fn_stations, args.fn_probs,
                         args.fn_times, args.fn_demands,
                         n_clusters=args.n_stations)
