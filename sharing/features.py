
import io
import time
import csv
import numpy as np
import sklearn.cluster as cluster


features_names = ["pickup_time", "dropoff_time", "passenger_count",
                  "pickup_station_lon", "pickup_station_lat",
                  "dropoff_station_lon", "dropoff_station_lat"]


def find_stations(fn_in, **kwargs):
    with io.open(fn_in, "rb") as fin:
        reader = csv.reader(fin)
        fl = sum(1 for _ in reader) - 1
    with io.open(fn_in, "rb") as fin:
        reader = csv.reader(fin)
        kmeans = cluster.KMeans(**kwargs)
        points = np.zeros((2 * fl, 2))
        for i, row in enumerate(reader):
            if i == 0:
                continue
            points[i - 1][0] = float(row[10])
            points[i - 1][1] = float(row[11])
            points[i - 1 + fl][0] = float(row[12])
            points[i - 1 + fl][1] = float(row[13])
        kmeans.fit(points)
        return kmeans, points


def percent_time(str_time):
    date_format = "%Y-%m-%d %H:%M:%S"
    t = time.strptime(str_time, date_format)
    secs = t.tm_hour * 60 * 60 + t.tm_min * 60 + t.tm_sec
    return secs / (24 * 60 * 60.0)


def extract_features(fn_in, fn_out):
    stations, points = find_stations(fn_in)
    with io.open(fn_in, "rb") as fin:
        with io.open(fn_out, "wb") as fout:
            reader = csv.reader(fin)
            writer = csv.writer(fout)
            for i, row in enumerate(reader):
                if i == 0:
                    writer.writerow(features_names)
                else:
                    features = [None] * len(features_names)
                    locs = np.array([[float(row[10]), float(row[11])],
                                     [float(row[12]), float(row[13])]])
                    sts = points[stations.predict(locs)]
                    features[0] = percent_time(row[5])
                    features[1] = percent_time(row[6])
                    features[2] = row[7]
                    features[3] = sts[0][0]
                    features[4] = sts[0][1]
                    features[5] = sts[1][0]
                    features[6] = sts[1][1]
                    writer.writerow(features)


if __name__ == "__main__":
    extract_features("data/trip_data_5_short.csv",
                     "data/trip_data_5_features.csv")
