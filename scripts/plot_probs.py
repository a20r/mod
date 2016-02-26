
import argparse
import csv
import io
import matplotlib.pyplot as plt
import common
import seaborn as sns
import pandas
import numpy as np
from numpy import median
from collections import defaultdict
from string import Template


DS = "Dropoff Station"
PR = "Probability"
MAP_TEMPLATE = "sandbox/map_template.html"
MAP_ACTUAL = "sandbox/map.html"
MAP_PICKUP_CUMULATIVE = "sandbox/map_pickup_cumulative.html"
MAP_DROPOFF_CUMULATIVE = "sandbox/map_dropoff_cumulative.html"


coord_template = Template(
    "{location: new google.maps.LatLng($lat, $lon), weight: $prob}")

latlon_template = Template("new google.maps.LatLng($lat, $lon)")


def normalize(probs):
    normed = dict()
    s = float(sum(probs.values()))
    for k in probs.keys():
        normed[k] = probs[k] / s
    return normed


def load_stations(fn_stations):
    sts = list()
    with io.open(fn_stations) as fin:
        reader = csv.reader(fin)
        next(reader)
        for row in reader:
            sts.append([float(row[2]), float(row[1])])
    return np.array(sts)


def load_probs(fn_probs, interval_min, interval_max, weekdays, pickup,
               n_keep=-1):
    probs = dict()
    probs[DS] = list()
    probs[PR] = list()
    dd = defaultdict(float)
    with io.open(fn_probs, "rb") as fin:
        reader = csv.DictReader(fin)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            row = common.clean_dict(row)
            int_within = interval_min <= row["tau"] <= interval_max
            wd_eq = row["day"] == weekdays
            pickup_eq = row["pickup"] == pickup
            if int_within and wd_eq and pickup_eq:
                dd[row["dropoff"]] += row["probability"]
        if n_keep > len(dd.values()):
            n_keep = len(dd.values())
        probs[DS] = map(int, dd.keys())[:n_keep]
        probs[PR] = dd.values()[:n_keep]
        return probs


def load_cumulative_probs(fn_probs, interval_min, interval_max, weekdays):
    dropoff_probs = defaultdict(float)
    pickup_probs = defaultdict(float)
    with io.open(fn_probs, "rb") as fin:
        reader = csv.DictReader(fin)
        next(reader)
        for row in reader:
            row = common.clean_dict(row)
            int_within = interval_min <= row["tau"] <= interval_max
            wd_eq = row["day"] in weekdays
            if int_within and wd_eq:
                dropoff_probs[row["dropoff"]] += row["probability"]
                pickup_probs[row["pickup"]] += row["probability"]
        return pickup_probs, dropoff_probs


def plot_probs_bar_graph(fn_probs, interval_min, interval_max, weekdays,
                         pickup, n_keep):
    probs = load_probs(
        fn_probs, interval_min, interval_max, weekdays, pickup, n_keep)
    probs[DS] = map(lambda v: "D" + str(v), probs[DS])
    probs = pandas.DataFrame(data=probs)
    sorty = sorted(zip(probs[DS], probs[PR]), key=lambda v: -v[1])
    order, ps = zip(*sorty)
    sns.barplot(x=PR, y=DS, data=probs, order=order, estimator=median, ci=0)
    plt.title("Top {} Most Likely Drop-off Stations from Pick-up Station {}"
              .format(n_keep, pickup))
    plt.xlabel("Likelihood")


def plot_heatmap(fn_probs, fn_stations, interval_min, interval_max,
                 weekdays, pickup):
    with open(MAP_TEMPLATE, "rb") as fin:
        template = Template(fin.read())
        p_args = [fn_probs, interval_min, interval_max, weekdays, pickup]
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
        pickup_gmaps = latlon_template.substitute(lat=p_lat, lon=p_lon)
        map_html = template.substitute(coords=",".join(c for c in coords),
                                       pickup=pickup_gmaps)
        with open(MAP_ACTUAL, "wb") as fout:
            fout.write(map_html)


def plot_cumulative_heatmap(probs, sts, fn_html):
    with open(MAP_TEMPLATE, "rb") as fin:
        template = Template(fin.read())
        coords = list()
        probs = normalize(probs)
        for k in probs.keys():
            lat = sts[k][1]
            lon = sts[k][0]
            coord = coord_template.substitute(
                lat=lat, lon=lon, prob=70 * probs[k])
            coords.append(coord)
        map_html = template.substitute(coords=",".join(c for c in coords))
        with open(fn_html, "wb") as fout:
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
        "--weekdays", dest="weekdays", nargs="*", type=int,
        default=[0, 1, 2, 3],
        help="Day of the week for pickup probabilities.")
    parser.add_argument(
        "--pickup", dest="pickup", type=int, default=82,
        help="Pickup station used for the probability plot.")
    parser.add_argument(
        "--n_keep", dest="n_keep", type=int, default=50,
        help="Top k stations to plot")
    parser.add_argument(
        "--fn_stations", dest="fn_stations", type=str,
        default="data/stations.csv", help="Top k stations to plot")
    parser.add_argument(
        "--fn_pickup_map", dest="fn_pickup_map", type=str,
        default=MAP_PICKUP_CUMULATIVE, help="Output file for pickup HTML")
    parser.add_argument(
        "--fn_dropoff_map", dest="fn_dropoff_map", type=str,
        default=MAP_DROPOFF_CUMULATIVE, help="Output file for dropofff HTML")
    args = parser.parse_args()
    sts = load_stations(args.fn_stations)
    pp, dp = load_cumulative_probs(args.fn_probs, args.interval_min,
                                   args.interval_max, args.weekdays)
    plot_cumulative_heatmap(pp, sts, args.fn_pickup_map)
    plot_cumulative_heatmap(dp, sts, args.fn_dropoff_map)
