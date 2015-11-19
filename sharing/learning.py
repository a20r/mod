
import csv
import io
import pickle
import numpy as np
import sklearn.mixture as mixture
# import sklearn.metrics as metrics
# import sklearn.cross_validation as cv
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
        y = np.zeros((fl,))
        for i, row in enumerate(reader):
            if i == 0:
                continue
            X[i - 1][0] = row["p_time"]
            X[i - 1][1] = row["p_day"]
            X[i - 1][2] = row["p_station"]
            X[i - 1][3] = row["d_station"]
            y[i - 1] = row["passenger_count"]
        return X, y, fl


def train(fn_in, **kwargs):
    X, y, _ = training_matrices(fn_in)
    clf = mixture.DPGMM(**kwargs)
    clf.fit(X, y)
    return clf, clf.aic(X)


def write_clf(fn_out, clf):
    with open(fn_out, "w") as fout:
        pstr = pickle.dumps(clf)
        fout.write(pstr)


if __name__ == "__main__":
    clf, acc = train("data/trip_data_5_features_short.csv", n_components=6)
    write_clf("models/dpgmm.model", clf)
    print acc
