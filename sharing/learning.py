
import csv
import io
import pickle
import numpy as np
import sklearn.mixture as mixture
import sklearn.metrics as metrics
import sklearn.cross_validation as cv
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
    X, y, n = training_matrices(fn_in)
    kf = cv.KFold(n, n_folds=kwargs.get("folds", 5), shuffle=True)
    clfs = list()
    for train, test in kf:
        clf = mixture.DPGMM(**kwargs)
        clf.fit(X[train], y[train])
        preds = clf.predict(X[test])
        trues = y[test]
        print preds
        acc = metrics.mean_squared_error(trues, preds)
        clfs.append((clf, acc))
    return min(clfs, key=lambda v: v[1])


def write_clf(fn_out, clf):
    with open(fn_out, "w") as fout:
        pstr = pickle.dumps(clf)
        fout.write(pstr)


if __name__ == "__main__":
    clf, acc = train("data/trip_data_5_features.csv", n_components=6)
    write_clf("models/dpgmm.model", clf)
    print acc
