
# import sklearn
import csv
import io
import numpy as np


def reader_length(reader):
    fl = sum(1 for _ in reader) - 1
    reader.seek(0)
    return fl


def training_matrices(fn_in):
    with io.open(fn_in, "rb") as fin:
        reader = csv.reader(fin)
        fl = reader_length(reader)
        X = np.zeros((fl, 2))
        for i, row in enumerate(reader):
            if i == 0:
                continue
            X
