
import io
import time
import csv
import numpy as np
import sklearn.cluster as cluster


feature_names = ["p_time", "d_time", "p_day", "passenger_count",
                 "p_station_lon", "p_station_lat", "d_station_lon",
                 "d_station_lat", "p_station", "d_station"]


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
        return kmeans, points


def extract_features(fn_in, fn_out, **kwargs):
    """
    Extracts features from the in put file `fn_in` and writes the features
    as a csv file to `fn_out`
    """
    stations, points = find_stations(fn_in, **kwargs)
    with io.open(fn_in, "rb") as fin:
        with io.open(fn_out, "wb") as fout:
            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=feature_names)
            writer.writeheader()
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                try:
                    row = clean_dict(row)
                    features = dict()
                    locs = np.array([
                        [row["pickup_longitude"], row["pickup_latitude"]],
                        [row["dropoff_longitude"], row["dropoff_longitude"]]])
                    sts_inds = stations.predict(locs)
                    sts = points[sts_inds]
                    features["passenger_count"] = row["passenger_count"]
                    features["p_day"] = percent_time(row["pickup_datetime"])[1]
                    features["p_time"] = percent_time(
                        row["pickup_datetime"])[0]
                    features["d_time"] = percent_time(
                        row["dropoff_datetime"])[0]
                    features["p_station_lon"] = sts[0][0]
                    features["p_station_lat"] = sts[0][1]
                    features["d_station_lon"] = sts[1][0]
                    features["d_station_lat"] = sts[1][1]
                    features["p_station"] = sts_inds[0]
                    features["d_station"] = sts_inds[1]
                    writer.writerow(features)
                except ValueError:
                    pass


if __name__ == "__main__":
    extract_features("data/trip_data_5.csv",
                     "data/trip_data_5_features.csv",
                     n_clusters=30)
