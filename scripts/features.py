
import io
import time
import csv
import numpy as np
import sklearn.cluster as cluster
from collections import defaultdict


feature_names = ["p_time", "p_day", "passenger_count",
                 "p_station", "d_station"]

fn_stations_fields = ["id", "latitude", "longitude"]

fn_probs_fields = ["tau", "day", "pickup", "dropoff", "probability"]


def percent_time(str_time):
    """
    Given a string representation of a date, this returns the percent of the
    day that the time is (i.e. 0.5 would be 12 noon)
    """
    date_format = "%Y-%m-%d %H:%M:%S"
    t = time.strptime(str_time, date_format)
    secs = t.tm_hour * 60 * 60 + t.tm_min * 60 + t.tm_sec
    return secs / (24 * 60 * 60.0), t.tm_wday


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


def create_stations_file(fn_raw, fn_stations, **kwargs):
    kmeans = find_stations(fn_raw, **kwargs)
    with io.open(fn_stations, "wb") as fout:
        writer = csv.DictWriter(fout, fieldnames=fn_stations_fields)
        writer.writeheader()
        for i, center in enumerate(kmeans.cluster_centers_):
            row = dict()
            row["id"] = i
            row["latitude"] = center[0]
            row["longitude"] = center[0]
            writer.writerow(row)
    return kmeans


def extract_frequencies(fn_raw, kmeans):
    num_pd = defaultdict(lambda: defaultdict(float))
    num_ti = defaultdict(float)
    with io.open(fn_raw, "rb") as fin:
        reader = csv.DictReader(fin)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            try:
                row = clean_dict(row)
                p_time, p_day = percent_time(row["pickup_datetime"])
                d_time, d_day = percent_time(row["pickup_datetime"])
                p_l = [row["pickup_longitude"], row["pickup_latitude"]]
                d_l = [row["dropoff_longitude"], row["dropoff_longitude"]]
                locs = np.array([p_l, d_l])
                sts = kmeans.predict(locs)
                tau = int(4 * 24 * p_time)
                ti = (tau, p_day)
                num_pd[ti][(sts[0], sts[1])] += row["passenger_count"]
                num_ti[ti] += row["passenger_count"]
            except ValueError:
                pass
    return num_pd, num_ti


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


def create_feature_files(fn_raw, fn_stations, fn_probs, **kwargs):
    kmeans = create_stations_file(fn_raw, fn_stations, **kwargs)
    create_probs_file(fn_raw, fn_probs, kmeans)


if __name__ == "__main__":
    create_feature_files("data/trip_data_5_short.csv",
                         "data/trip_data_5_stations_short.csv",
                         "data/trip_data_5_probs_short.csv",
                         n_clusters=10)
