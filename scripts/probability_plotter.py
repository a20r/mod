
import argparse
import csv
import io
import matplotlib.pyplot as plt
import common
import seaborn as sns
import pandas
import numpy as np
from numpy import median


DS = "Dropoff Station"
PR = "Probability"


def load_probs(fn_probs, interval_min, interval_max, weekday, pickup):
    probs = dict()
    probs[DS] = list()
    probs[PR] = list()
    with io.open(fn_probs, "rb") as fin:
        reader = csv.DictReader(fin)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            row = common.clean_dict(row)
            int_within = interval_min <= row["tau"] <= interval_max
            wd_eq = row["day"] == weekday
            pickup_eq = row["pickup"] == pickup
            if int_within and wd_eq and pickup_eq:
                probs[DS].append("d" + str(int(row["dropoff"])))
                probs[PR].append(row["probability"])
        probs[DS] = np.array(probs[DS], dtype=str)
        probs[PR] = np.array(probs[PR], dtype=float)
        print len(probs[DS]), len(set(probs[DS]))
        return pandas.DataFrame(data=probs)


def plot_probs(fn_probs, interval_min, interval_max, weekday, pickup):
    probs = load_probs(fn_probs, interval_min, interval_max, weekday, pickup)
    sorty = sorted(zip(probs[DS], probs[PR]), key=lambda v: -v[1])
    order, ps = zip(*sorty)
    sns.barplot(x=PR, y=DS, data=probs, order=list(order), estimator=median, ci=0)


if __name__ == "__main__":
    sns.set_context("poster")
    parser = argparse.ArgumentParser(
        description="Plot the probability of a given requests.")
    parser.add_argument(
        "--fn_probs", dest="fn_probs", type=str,
        default="data/probs.csv",
        help="CSV of probabilities for given requests.")
    parser.add_argument(
        "--interval_min", dest="interval_min", type=int, default=0,
        help="Minimum interval for the probability plot.")
    parser.add_argument(
        "--interval_max", dest="interval_max", type=int, default=95,
        help="Maximum interval for the probability plot.")
    parser.add_argument(
        "--weekday", dest="weekday", type=int, default=4,
        help="Day of the week for pickup probabilities.")
    parser.add_argument(
        "--pickup", dest="pickup", type=int, default=2,
        help="Pickup station used for the probability plot.")
    args = parser.parse_args()
    plot_probs(args.fn_probs, args.interval_min, args.interval_max,
               args.weekday, args.pickup)
    plt.show()
