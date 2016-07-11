
import argparse
import common
import numpy as np
import matplotlib
import pandas as pd
matplotlib.use("Agg")
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import seaborn as sns
import tabler
from datetime import datetime
from itertools import product
from table_common import table_header, line_tp, table_footer
from collections import defaultdict

instances = [(500, 1, 0), (500, 2, 0), (500, 3, 0), (500, 4, 0),
             (125, 4, 0), (250, 4, 0), (375, 4, 0), (625, 4, 0),
             (750, 4, 0), (1000, 4, 0), (250, 4, 1), (375, 4, 1),
             (500, 4, 1), (625, 4, 1), (750, 4, 1)]


n_vecs = [125, 250, 375, 500, 625, 750, 1000]
predictions = ["0-nR", 0, 100, 200, 300, 400]
waiting_times = [120, 300, 420]
vehicles = [1000, 2000, 3000]
fields = ["mean_waiting_time", "mean_passengers", "mean_delay", "n_pickups",
          "mean_travel_delay", "serviced_percentage", "total_km_travelled",
          "km_travelled_per_car", "empty_rebalancing",
          "empty_moving_to_pickup", "empty_waiting", "not_empty",
          "active_taxis", "n_shared", "n_shared_perc"]
caps = [1, 2, 4, 10]
clrs = [sns.xkcd_rgb["grey"], sns.xkcd_rgb["sky blue"],
        sns.xkcd_rgb["bright red"], sns.xkcd_rgb["black"]]
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday"]


def print_here(pargs=True):
    def dec(f):
        def __inner(*args, **kwargs):
            very_big = 1000
            print "Executing:", f.func_name
            if pargs:
                n_args = f.func_code.co_argcount
                print "With Args:"
                for i, v in enumerate(f.func_code.co_varnames[:n_args]):
                    astr = repr(args[i])
                    if len(astr) > very_big:
                        astr = type(args[i])
                    print "\t", v, ":", astr
                print "With Kwargs:",
                if len(kwargs.keys()) > 0:
                    print ""
                    for key in kwargs:
                        kwstr = repr(kwargs[key])
                        if len(kwstr) > very_big:
                            kwstr = type(kwargs[key])
                        print "\t", key, ":", kwstr
                else:
                    print "None"
            return f(*args, **kwargs)
        return __inner
    return dec


def prettify(text):
    if text == "n_pickups":
        return "Number of Pickups"
    if text == "n_shared":
        return "Number of Shared Rides"
    if text == "n_shared_per_passenger":
        return "Num Shared / Passenger"
    if text == "mean_waiting_time":
        return "Mean Waiting Time [s]"
    if text == "mean_delay":
        return "Mean Delay [s]"
    if text == "mean_travel_delay":
        return "Mean Travel Delay [s]"
    if text == "n_shared_perc":
        return "% of Shared Trips"
    if text == "km_travelled_per_car":
        return "Mean Distance Travelled [km]"
    if text == "serviced_percentage":
        return "% of Serviced Requests"
    else:
        words = text.split("_")
        return " ".join(w.capitalize() for w in words)


def make_wt_title(vec):
    return "N.V: {}".format(vec)


def make_vec_title(wt):
    return "M.W.T: {}".format(wt)


def make_pred_title(wt, cap):
    return "M.W.T: {}, Cap: {}".format(wt, cap)


def create_latex_table(df):
    lines = list()
    for i, (n_vecs, cap, rb) in enumerate(instances):
        st = df
        n_hrs = common.MAX_SECONDS / (60 * 60.0)
        pickups = np.sum(st["n_pickups"]) / n_hrs
        ignored = np.sum(st["n_ignored"]) / n_hrs
        pickups_std = 3600 * np.std(st["n_pickups"]) / common.MAX_SECONDS
        ignored_std = 3600 * np.std(st["n_ignored"]) / common.MAX_SECONDS
        waiting_time = np.mean(st["mean_waiting_time"])
        waiting_time_std = np.std(st["mean_waiting_time"])
        delay = np.mean(st["mean_delay"])
        delay_std = np.std(st["mean_delay"])
        occupancy = np.mean(st["mean_passengers"])
        occupancy_std = np.std(st["mean_passengers"])
        line = line_tp.format(
            i + 1, n_vecs, cap, pickups, pickups_std,
            ignored, ignored_std, waiting_time, waiting_time_std,
            delay, delay_std, occupancy, occupancy_std)
        lines.append(line)
    inner_lines = "\n\\hline\n".join(line for line in lines)
    return table_header + inner_lines + table_footer


def is_first_10_mins(t):
    return t.hour == 0 and t.minute <= 10


def plot_ts(df, field, *args, **kwargs):
    dates = df["time"]
    values = df[field]
    vals = list()
    dts = list()
    for i in xrange(len(dates)):
        dt = datetime.strptime(dates.iloc[i], common.date_format)
        if not is_first_10_mins(dt):
            dts.append(dt)
            vals.append(values.iloc[i])
    dts = matplotlib.dates.date2num(dts)
    return plt.plot_date(dts, vals, *args, **kwargs)


def set_legend_marker_size(lgd, size):
    for i in xrange(len(lgd.legendHandles)):
        lgd.legendHandles[i]._legmarker.set_markersize(size)


def set_legend_linewidth(lgd, lw):
    for i in xrange(len(lgd.legendHandles)):
        lgd.legendHandles[i].set_linewidth(lw)


@print_here()
def make_ts_plot(vecs, wt, rb, field):
    fmt = DateFormatter("%a")
    fig, ax = plt.subplots()
    fig.set_size_inches(13, 10)
    for cap, clr in zip(caps, clrs):
        df = tabler.get_metrics(vecs, cap, wt, 0)
        locs, labels = plt.xticks()
        plot_ts(df, field, "o", color=clr, alpha=1,
                label=str(cap))
    ax.xaxis.set_major_formatter(fmt)
    lgd = plt.legend(loc="center left", fancybox=True,
                     shadow=True, bbox_to_anchor=(1, 0.5),
                     title="Capacity")
    set_legend_marker_size(lgd, 40)
    plt.ylabel(prettify(field))
    fig.autofmt_xdate()
    plt.title("N. Vecs: {}, M.W.T: {}".format(vecs, wt))
    plt.savefig("figs/ts-{}-v{}-w{}.png".format(field, vecs, wt),
                bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()


@print_here()
def make_ts_area_plot(vecs, cap, wt, rb):
    plt.figure()
    df = tabler.get_metrics(vecs, cap, wt, rb)
    subfields = ["empty_waiting", "empty_rebalancing",
                 "empty_moving_to_pickup"]
    subfields.extend(["time_pass_%d" % i for i in xrange(1, cap + 1)])
    df_small = df[subfields].copy()
    ax = df_small.plot(kind="area", colormap="rainbow",
                       figsize=(13, 10))
    labels = ["Waiting", "Rebalancing", "Picking Up"]
    labels.extend(["N. Pass: %d" % n for n in xrange(1, cap + 1)])
    handles, _ = ax.get_legend_handles_labels()
    lgd = ax.legend(reversed(handles),
                    reversed(labels),
                    loc='center left',
                    bbox_to_anchor=(1.0, 0.5))
    set_legend_linewidth(lgd, 30)
    d_str = "N. Vecs: {}, Cap: {}, M.W.T: {}".format(vecs, cap, wt, rb)
    ax.set_title("Vehicle Occupancy Over Time \nw/ " + d_str)
    max_x_ticks = ax.get_xticks()[-1]
    ax.set_xticks(np.linspace(0, max_x_ticks - 4720, 8))
    dr = pd.date_range(start="05-05-13", periods=len(ax.get_xticks()))
    dr = dr.map(lambda t: t.strftime("%a"))
    ax.set_xticklabels(dr)
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:3.0f}%'.format(x / 10) for x in vals])
    ax.set_xlabel("Time")
    plt.savefig("figs/ts-area-v{}-c{}-w{}.png".format(vecs, cap, wt),
                bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()


@print_here()
def make_ts_area_plot_single(vecs, cap, wt, rb, weekday):
    plt.figure()
    df = tabler.get_metrics(vecs, cap, wt, rb)
    subfields = ["empty_waiting", "empty_rebalancing",
                 "empty_moving_to_pickup"]
    subfields.extend(["time_pass_%d" % i for i in xrange(1, cap + 1)])
    df_small = df[subfields].copy()
    q_str = "{0} * 2878 <= index <= ({0} + 1) * 2878".format(weekday)
    df_small = df_small.query(q_str)
    df_small.index = range(2879)
    ax = df_small.plot(kind="area", colormap="rainbow",
                       figsize=(13, 10))
    labels = ["Waiting", "Rebalancing", "Picking Up"]
    labels.extend(["N. Pass: %d" % n for n in xrange(1, cap + 1)])
    handles, _ = ax.get_legend_handles_labels()
    lgd = ax.legend(reversed(handles),
                    reversed(labels),
                    loc='center left',
                    bbox_to_anchor=(1.0, 0.5))
    set_legend_linewidth(lgd, 30)
    d_str = "N. Vecs: {}, Cap: {}, M.W.T: {}".format(vecs, cap, wt)
    t_str = "Vehicle Occupancy Over Time On {} \n w/ ".format(days[weekday])
    ax.set_title(t_str + d_str)
    max_x_ticks = ax.get_xticks()[-1]
    ax.set_xticks(np.arange(0, max_x_ticks, max_x_ticks / 13))
    dr = pd.date_range(start="05-05-16", periods=len(ax.get_xticks()),
                       freq="2H")
    dr = dr.map(lambda t: t.strftime("%H"))
    ax.set_xticklabels(dr)
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:3.0f}%'.format((x / 10) / (vecs / 1000))
                        for x in vals])
    ax.set_xlabel("Hour")
    plt.savefig(
        "figs/ts-area-v{}-c{}-w{}-{}.png".format(vecs, cap, wt, days[weekday]),
        bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()


@print_here(False)
def get_avg_dataframe():
    cols = ["predictions", "vehicles", "waiting_time", "capacity"] + fields \
        + map(lambda f: f + "_std", fields) + ["n_shared_per_passenger"]
    data = pd.DataFrame(columns=cols)
    counter = 0
    gen = product(predictions, vehicles, caps, waiting_times)
    for (p, v, cap, wt) in gen:
        f_vals = list()
        f_stds = list()
        try:
            df = tabler.get_metrics(v, cap, wt, p)
            for field in fields:
                f_vals.append(np.mean(df[field]))
                f_stds.append(np.std(df[field]))
            data.loc[counter] = [p, int(v), int(wt), int(cap)] \
                + f_vals + f_stds \
                + [df["n_shared"].sum() / df["n_pickups"].sum()]
            counter += 1
        except IOError:
            pass
    return data


@print_here(False)
def make_avg_plots_with_preds(big_d):
    d = big_d.query("capacity == 4 and waiting_time == 300")
    cap, wt = 4, 300
    fig = plt.figure()
    fig.set_size_inches(13, 10)
    for field in fields:
        ax = sns.pointplot(x="vehicles", y=field, hue="predictions", data=d)
        ax.set_xticklabels(vehicles)
        plt.ylabel(prettify(field))
        plt.xlabel("Num Vehicles")
        handles, _ = ax.get_legend_handles_labels()
        plt.legend(
            handles,
            ["No R.B.", 0, 100, 200, 300, 400],
            loc="center left", fancybox=True,
            shadow=True, bbox_to_anchor=(1, 0.5),
            title="Predictions", markerscale=3)
        plt.title(make_pred_title(wt, cap))
        plt.savefig(
            "figs/avg-with-preds-{}.png".format(field),
            bbox_inches='tight')
        plt.close()


@print_here()
def make_avg_plots(big_d, plot_type):
    plot_params = {"vecs": (waiting_times, "waiting_time", "vehicles",
                            "Number of Vehicles", vehicles,
                            make_vec_title,
                            fields + ["n_shared_per_passenger"]),
                   "wts": (vehicles, "vehicles", "waiting_time",
                           "Max Waiting Time", waiting_times,
                           make_wt_title,
                           fields + ["n_shared_per_passenger"]),
                   "comp_times": (waiting_times, "waiting_time", "vehicles",
                                  "Number of Vehicles", vehicles,
                                  make_vec_title, ["comp_time"])}
    iover, qstr, xcol, xlabel, xticklabels, tfunc, fs = plot_params[plot_type]
    for field in fields + ["n_shared_per_passenger"]:
        max_val = None
        min_val = None
        axes = list()
        fig = plt.figure()
        fig.set_size_inches(18, 8)
        for i, v in enumerate(iover, start=1):
            plt.subplot(1, len(iover), i)
            q = "predictions == 0 and {} == {}".format(qstr, v)
            d = big_d.query(q)
            ax = sns.pointplot(x=xcol, y=field, hue="capacity", data=d,
                               palette=clrs)
            ax.grid("on")
            ax.set_title(tfunc(v))
            axes.append(ax)
            ax.legend().remove()
            ax.set_xticklabels(xticklabels)
            if i == 1:
                plt.ylabel(prettify(field))
            else:
                plt.ylabel("")
            if i == 2:
                plt.xlabel(xlabel)
            else:
                plt.xlabel("")
            if i > 1:
                ax.get_yaxis().set_ticklabels([])
            if i == len(waiting_times):
                handles, _ = ax.get_legend_handles_labels()
                plt.legend(
                    handles,
                    [1, 2, 4, 10],
                    loc="center left", fancybox=True,
                    shadow=True, bbox_to_anchor=(1, 0.5),
                    title="Capacities", markerscale=3)
            if max_val is None or max_val < max(d[field]):
                max_val = max(d[field])
            if min_val is None or min_val > min(d[field]):
                min_val = min(d[field])
        for ax in axes:
            ax.set_ylim(min_val - 0.1 * max_val, 1.1 * max_val)
        filename = "figs/avg-with-{}-{}.png".format(plot_type, field)
        plt.savefig(filename, bbox_inches='tight')
        plt.close()


@print_here(False)
def make_empty_type_plots(big_d):
    plt.figure()
    data = defaultdict(list)
    empty_fields = ["empty_rebalancing", "empty_moving_to_pickup",
                    "empty_waiting", "not_empty"]
    data["Empty Type"] = empty_fields
    for ef in empty_fields:
        data["Number of Trips"].append(big_d[ef].sum())
    df = pd.DataFrame(data)
    sns.barplot(x="Empty Type", y="Number of Trips", data=df)
    filename = "figs/empty_type_bar_plot.png"
    plt.savefig(filename, bbox_inches="tight")
    plt.close()


@print_here(False)
def make_all_ts_plots():
    for v, wt, f in product(vehicles, waiting_times, fields):
        make_ts_plot(v, wt, 0, f)


@print_here(False)
def make_all_ts_area_plots():
    for v, c, wt in product(vehicles, caps, waiting_times):
        make_ts_area_plot(v, c, wt, 0)


@print_here(False)
def make_all_ts_area_single_plots():
    for v, c, wt, wd in product(vehicles, caps, waiting_times, xrange(7)):
        make_ts_area_plot_single(v, c, wt, 0, wd)


@print_here(False)
def make_all_comp_times_plots():
    df = pd.read_csv("data/times.csv")
    for wt, day in product(waiting_times, range(7)):
        make_comp_times_plot(df, wt, day)
    for wt in waiting_times:
        make_avg_comp_times_plot(df, wt)


@print_here()
def make_comp_times_plot(df, wt, day):
    plt.figure()
    df_small = df.query("waiting_time == {} and day == {}".format(wt, day))
    ax = sns.pointplot(x="vehicles", y="comp_time", hue="capacity",
                       data=df_small, palette=clrs)
    ax.set_xticklabels(vehicles)
    ax.set_xlabel("Number of Vehicles")
    ax.set_ylabel("Computational Time [hr]")
    ax.set_ylim(0, 1.05 * max(df_small["comp_time"]))
    plt.title("M.W.T: {}, Day: {}".format(wt, days[day]))
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:3.1f}'.format(x) for x in vals])
    handles, _ = ax.get_legend_handles_labels()
    plt.legend(
        handles,
        [1, 2, 4, 10],
        loc="center left", fancybox=True,
        shadow=True, bbox_to_anchor=(1, 0.5),
        title="Capacities", markerscale=3)
    filename = "figs/comp-time-w{}-{}.png".format(wt, days[day])
    plt.savefig(filename, bbox_inches='tight')
    plt.close()


@print_here()
def make_avg_comp_times_plot(df, wt):
    plt.figure()
    df_small = df.query("waiting_time == {}".format(wt))
    ax = sns.pointplot(x="vehicles", y="comp_time", hue="capacity",
                       data=df_small, palette=clrs)
    ax.set_xticklabels(vehicles)
    ax.set_xlabel("Number of Vehicles")
    ax.set_ylabel("Avg. Computational Time [hr]")
    # ax.set_ylim(0, 1.05 * max(df_small["comp_time"]))
    plt.title("M.W.T: {}".format(wt))
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:3.1f}'.format(x) for x in vals])
    handles, _ = ax.get_legend_handles_labels()
    plt.legend(
        handles,
        [1, 2, 4, 10],
        loc="center left", fancybox=True,
        shadow=True, bbox_to_anchor=(1, 0.5),
        title="Capacities", markerscale=3)
    filename = "figs/comp-time-w{}.png".format(wt)
    plt.savefig(filename, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    plt.ioff()
    sns.set_context("poster", font_scale=2)
    parser = argparse.ArgumentParser(
        description=("Creates plots plots for MOD"))
    parser.add_argument(
        "--plot_type", dest="plot_type", type=str,
        help=("Specifies the type of plot to generate. "
              "The options are 'area', 'area_single_day'"
              ", 'avg', 'comp_times', or 'ts'"))
    args = parser.parse_args()
    plots = {"area": [make_all_ts_area_plots],
             "area_single_day": [make_all_ts_area_single_plots],
             "avg": [make_avg_plots_with_preds,
                     lambda d: make_avg_plots(d, "vecs"),
                     lambda d: make_avg_plots(d, "wts"),
                     lambda d: make_avg_plots(d, "comp_times"),
                     make_empty_type_plots],
             "ts": [make_all_ts_plots],
             "comp_times": [make_all_comp_times_plots]}
    if args.plot_type == "avg":
        big_d = get_avg_dataframe()
        for func in plots["avg"]:
            func(big_d)
    else:
        for func in plots[args.plot_type]:
            func()
