
import argparse
import csv
import io
import matplotlib.pyplot as plt
import common
import seaborn as sns
import pandas
import numpy as np
import math
from numpy import median
from collections import defaultdict
from string import Template


DS = "Dropoff Station"
PR = "Probability"
MAP_TEMPLATE = "sandbox/map_template.html"
MAP_ACTUAL = "sandbox/map.html"


coord_template = Template(
    "{location: new google.maps.LatLng($lat, $lon), weight: $prob}")

latlon_template = Template("new google.maps.LatLng($lat, $lon)")


def meanify(dofl):
    for k in dofl.keys():
        dofl[k] = np.mean(dofl[k])
    return dofl


def load_stations(fn_stations):
    sts = list()
    with io.open(fn_stations) as fin:
        reader = csv.reader(fin)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            sts.append([float(row[2]), float(row[1])])
    return np.array(sts)

def load_probs(fn_probs, interval_min, interval_max, weekday, pickup,
               n_keep=-1):
    probs = dict()
    probs[DS] = list()
    probs[PR] = list()
    dd = defaultdict(list)
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
                dd[row["dropoff"]].append(row["probability"])
        dd = meanify(dd)
        if n_keep > len(dd.values()):
            n_keep = len(dd.values())
        probs[DS] = map(int, dd.keys())[:n_keep]
        probs[PR] = dd.values()[:n_keep]
        return probs


def plot_probs_bar_graph(fn_probs, interval_min, interval_max, weekday, pickup,
                         n_keep):
    probs = load_probs(
        fn_probs, interval_min, interval_max, weekday, pickup, n_keep)
    probs[DS] = map(lambda v: "D" + str(v), probs[DS])
    probs = pandas.DataFrame(data=probs)
    sorty = sorted(zip(probs[DS], probs[PR]), key=lambda v: -v[1])
    order, ps = zip(*sorty)
    sns.barplot(x=PR, y=DS, data=probs, order=order, estimator=median, ci=0)
    plt.title("Top {} Most Likely Drop-off Stations from Pick-up Station {}"\
              .format(n_keep, pickup))
    plt.xlabel("Likelihood")


def normalize(probs):
    normed = list()
    s = float(sum(probs))
    for p in probs:
        normed.append(p / s)
    return normed


def plot_heatmap(fn_probs, fn_stations, interval_min, interval_max,
                 weekday, pickup):
    with open(MAP_TEMPLATE, "rb") as fin:
        template = Template(fin.read())
        p_args = [fn_probs, interval_min, interval_max, weekday, pickup]
        probs = load_probs(*p_args)
        sts = load_stations(fn_stations)
        coords = list()
        normed = normalize(probs[PR])
        for i in xrange(len(probs[DS])):
            lat = sts[probs[DS][i]][1]
            lon = sts[probs[DS][i]][0]
            prob = normed[i]
            coord = coord_template.substitute(
                lat=lat, lon=lon, prob=100 * prob)
            coords.append(coord)
        p_lat = sts[pickup][1]
        p_lon = sts[pickup][0]
        pickup_gmaps = latlon_template.substitute(lat=lat, lon=lon)
        map_html = template.substitute(coords=",".join(c for c in coords),
                                       pickup=pickup_gmaps)
        with open(MAP_ACTUAL, "wb") as fout:
            fout.write(map_html)


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
        "--pickup", dest="pickup", type=int, default=82,
        help="Pickup station used for the probability plot.")
    parser.add_argument(
        "--n_keep", dest="n_keep", type=int, default=50,
        help="Top k stations to plot")
    parser.add_argument(
        "--fn_stations", dest="fn_stations", type=str,
        default="data/stationsLUT.csv", help="Top k stations to plot")
    args = parser.parse_args()
    plot_heatmap(args.fn_probs, args.fn_stations, args.interval_min,
                 args.interval_max, args.weekday, args.pickup)
    plot_probs_bar_graph(args.fn_probs, args.interval_min, args.interval_max,
                         args.weekday, args.pickup, args.n_keep)
    plt.show()
