
# import sklearn
import csv
import io
import numpy as np
from features import feature_names


def reader_length(reader):
    fl = sum(1 for _ in reader) - 1
    return fl


def training_matrices(fn_in):
    with io.open(fn_in, "rb") as fin:
        reader = csv.DictReader(fin, fieldnames=feature_names)
        fl = reader_length(reader)
        fin.seek(0)
        X = np.zeros((fl, 4))
        Y = np.zeros((fl, 1))
        for i, row in enumerate(reader):
            if i == 0:
                continue
            X[i - 1][0] = row["p_time"]
            X[i - 1][1] = row["p_day"]
            X[i - 1][2] = row["p_station"]
            X[i - 1][3] = row["d_station"]
            Y[i - 1] = row["passenger_count"]
        return X, Y


def learn(fn_in):
    pass


if __name__ == "__main__":
    training_matrices("data/trip_data_5_features_short.csv")
