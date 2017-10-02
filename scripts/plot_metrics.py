
import argparse
import common
import numpy as np
import matplotlib
import pandas as pd
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from common import get_metrics
from datetime import datetime
from itertools import product
from collections import defaultdict
from tqdm import tqdm


aux_fig_size = (5, 3)
hours = ["same", "t12", "t19"]
demands = ["half", "same", "double"]
intervals = [10, 20, 30, 40, 50]
predictions = ["0-nR", 0, 100, 200, 300, 400]
waiting_times = [120, 300, 420]
vehicles = [1000, 2000, 3000]
fields = ["mean_waiting_time", "mean_passengers", "mean_delay", "n_pickups",
          "mean_travel_delay", "serviced_percentage", "total_km_travelled",
          "km_travelled_per_car", "empty_rebalancing",
          "empty_moving_to_pickup", "empty_waiting", "not_empty",
          "active_taxis", "n_shared"]
caps = [1, 2, 4, 10]
clrs = [sns.xkcd_rgb["grey"], sns.xkcd_rgb["sky blue"],
        sns.xkcd_rgb["bright red"], sns.xkcd_rgb["black"]]
dem_clrs = [sns.xkcd_rgb["grey"], sns.xkcd_rgb["bright red"]]
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
        return "% of Shared Rides"
    if text == "mean_waiting_time":
        return "Mean Waiting Time [s]"
    if text == "mean_delay":
        return "Mean Delay [s]"
    if text == "mean_travel_delay":
        return "Mean Travel Delay [s]"
    if text == "n_shared_perc":
        return "% of Shared Trips"
    if text == "km_travelled_per_car":
        return "Mean Travel [km]"
    if text == "serviced_percentage":
        return "% Serviced Requests"
    if text == "comp_time":
        return "Mean Comp. Time [s]"
    if text == "interval":
        return "Step Size [s]"
    else:
        words = text.split("_")
        return " ".join(w.capitalize() for w in words)


def make_wt_title(vec):
    return "m={}".format(vec)


def make_vec_title(wt):
    return "M.W.T: {}".format(wt)


def make_pred_title(wt, cap):
    return "M.W.T: {}, Cap: {}".format(wt, cap)


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
    return plt.plot_date(dts, vals, *args, **kwargs), dts


def set_legend_marker_size(lgd, size):
    for i in xrange(len(lgd.legendHandles)):
        lgd.legendHandles[i]._legmarker.set_markersize(size)


def set_legend_linewidth(lgd, lw):
    for i in xrange(len(lgd.legendHandles)):
        lgd.legendHandles[i].set_linewidth(lw)
        lgd.legendHandles[i].set_linestyle(":")


@print_here()
def make_ts_plot(vecs, wt, rb, field):
    # fmt = DateFormatter("%a")
    # matplotlib.rc("font", weight="bold")
    # matplotlib.rc("axes", labelweight="bold")
    # matplotlib.rc("figure", titleweight="bold")
    fig, ax = plt.subplots()
    fig.set_size_inches(4, 2.46)
    for cap, clr in zip(caps, clrs):
        df = get_metrics(vecs, cap, wt, 0)
        locs, labels = plt.xticks()
        _, dts = plot_ts(df, field, "o", color=clr, alpha=1,
                         label=str(cap), markersize=4)
    ticks = [min(dts)] + list(ax.get_xticks()) + [max(dts)]
    new_ticks = list()
    for i in xrange(len(ticks) - 1):
        new_ticks.append(ticks[i])
        new_ticks.append(0.5 * (ticks[i] + ticks[i + 1]))
    new_ticks.append(ticks[-1])
    ax.set_xticks(new_ticks)
    ticklabels = "| Su | Mo | Tu | We | Th | Fr | Sa |".split(" ")
    ax.set_xticklabels(ticklabels)
    lgd = plt.legend(loc="center left", fancybox=True,
                     shadow=True, bbox_to_anchor=(1, 0.5),
                     title="Capacity")
    lgd.get_title().set_fontsize(15)
    set_legend_marker_size(lgd, 15)
    plt.ylabel(prettify(field))
    if "%" in prettify(field):
        ax.set_ylim([0, 1])
        vals = ax.get_yticks()
        ax.set_yticklabels(['{:3.0f}%'.format(x * 100) for x in vals])
    # fig.autofmt_xdate()
    # plt.title("N. Vecs: {}, M.W.T: {}".format(vecs, wt))
    plt.savefig("figs/ts-{}-v{}-w{}.png".format(field, vecs, wt),
                bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()


def fix_area_handles(handles):
    new_handles = list()
    for h in handles:
        nh = Line2D([], [], marker="o", markerfacecolor=h.get_color(),
                    markersize=15, linestyle='None')
        new_handles.append(nh)
    return new_handles


@print_here()
def make_ts_area_plot(vecs, cap, wt, rb):
    plt.figure()
    df = get_metrics(vecs, cap, wt, rb)
    subfields = ["empty_waiting", "empty_rebalancing",
                 "empty_moving_to_pickup"]
    subfields.extend(["time_pass_%d" % i for i in xrange(1, cap + 1)])
    df_small = df[subfields].copy()
    ax = df_small.plot(kind="area", colormap="rainbow",
                       figsize=(4, 2.2))
    labels = ["Waiting", "Rebalancing", "Picking Up"]
    labels.extend(["N. Pass: %d" % n for n in xrange(1, cap + 1)])
    handles, _ = ax.get_legend_handles_labels()
    handles = fix_area_handles(handles)
    lgd = ax.legend(reversed(handles),
                    reversed(labels),
                    loc='center left',
                    bbox_to_anchor=(1.0, 0.5),
                    borderaxespad=0,
                    handletextpad=0)
    d_str = "N. Vecs: {}, Cap: {}, M.W.T: {}".format(vecs, cap, wt, rb)
    ax.set_title("Vehicle Occupancy Over Time \nw/ " + d_str)
    max_x_ticks = ax.get_xticks()[-1]
    ax.set_xticks(np.linspace(0, max_x_ticks - 4720, 8))
    dr = pd.date_range(start="05-05-13", periods=len(ax.get_xticks()))
    dr = dr.map(lambda t: t.strftime("%a"))
    ax.set_xticklabels(dr)
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:3.0f}%'.format(x / 10) for x in vals])
    # ax.set_xlabel("Time")
    plt.savefig("figs/ts-area-v{}-c{}-w{}.png".format(vecs, cap, wt),
                bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()


@print_here()
def make_ts_area_plot_single(vecs, cap, wt, rb, weekday):
    # sns.set_context("poster", font_scale=2)
    plt.figure()
    df = get_metrics(vecs, cap, wt, rb)
    subfields = ["empty_waiting", "empty_rebalancing",
                 "empty_moving_to_pickup"]
    subfields.extend(["time_pass_%d" % i for i in xrange(1, cap + 1)])
    df_small = df[subfields].copy()
    q_str = "{0} * 2878 <= index <= ({0} + 1) * 2878".format(weekday)
    df_small = df_small.query(q_str)
    df_small.index = range(2879)
    ax = df_small.plot(kind="area", colormap="rainbow",
                       figsize=(4, 2.2))
    labels = ["Waiting", "Rebalancing", "Picking Up"]
    labels.extend(["N. Pass: %d" % n for n in xrange(1, cap + 1)])
    handles, _ = ax.get_legend_handles_labels()
    handles = fix_area_handles(handles)
    lgd = ax.legend(reversed(handles),
                    reversed(labels),
                    loc='center left',
                    bbox_to_anchor=(1.0, 0.5),
                    borderaxespad=0,
                    handletextpad=0)
    d_str = "N. Vecs: {}, Cap: {}, M.W.T: {}".format(vecs, cap, wt)
    t_str = "Vehicle Occupancy Over Time On {} \n w/ ".format(days[weekday])
    ax.set_title(t_str + d_str)
    max_x_ticks = ax.get_xticks()[-1]
    ax.set_xticks(np.arange(0, max_x_ticks, max_x_ticks / 6))
    dr = pd.date_range(start="05-05-16", periods=len(ax.get_xticks()),
                       freq="4H")
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
        + ["n_shared_per_passenger"]
    data = pd.DataFrame(columns=cols)
    counter = 0
    gen = product(predictions, vehicles, caps, waiting_times)
    for (p, v, cap, wt) in gen:
        f_vals = list()
        try:
            df = get_metrics(v, cap, wt, p)
            for field in fields:
                if field == "km_travelled_per_car":
                    last_entries = df[df.time.str.contains("23:59:00")]
                    val = np.mean(last_entries["km_travelled_per_car"])
                    f_vals.append(val)
                else:
                    f_vals.append(np.mean(df[field]))
            data.loc[counter] = [p, int(v), int(wt), int(cap)] \
                + f_vals \
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
    for field in fields + ["n_shared_per_passenger"]:
        ax = sns.pointplot(x="vehicles", y=field, hue="predictions", data=d)
        ax.set_xticklabels(vehicles)
        plt.ylabel(prettify(field))
        if "%" in prettify(field):
            ax.set_ylim([0, 1])
            vals = ax.get_yticks()
            ax.set_yticklabels(['{:3.0f}%'.format(x * 100) for x in vals])
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
                           "Max Waiting Time [min]", [2, 5, 7],
                           make_wt_title,
                           fields + ["n_shared_per_passenger"]),
                   "comp_times": (vehicles, "vehicles", "waiting_time",
                                  "Max Waiting Time [min]", [2, 5, 7],
                                  make_wt_title, ["comp_time"])}
    iover, qstr, xcol, xlabel, xticklabels, tfunc, fs = plot_params[plot_type]
    # for field in fs:
    for field in ["km_travelled_per_car", "mean_waiting_time"]:
        max_val = None
        min_val = None
        axes = list()
        fig = plt.figure()
        fig.set_size_inches(1.3 * 3.2, 1.5)
        for i, v in enumerate(iover, start=1):
            plt.subplot(1, len(iover), i)
            plt.subplots_adjust(wspace=0.08)
            if plot_type == "comp_times":
                q = "{} == {}".format(qstr, v)
            else:
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
                if "%" in prettify(field):
                    ax.set_ylim(0, 1)
                    vals = ax.get_yticks()
                    yticklabels = ['{:3.0f}%'.format(x * 100) for x in vals]
                    ax.set_yticklabels(yticklabels)
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
                lgd = plt.legend(
                    handles,
                    [1, 2, 4, 10],
                    loc="center left", fancybox=True,
                    shadow=True, bbox_to_anchor=(1, 0.5),
                    title="Capacity", markerscale=2,
                    borderaxespad=0,
                    handletextpad=0)
                lgd.get_title().set_fontsize(12)
            if max_val is None or max_val < max(d[field]):
                max_val = max(d[field])
            if min_val is None or min_val > min(d[field]):
                min_val = min(d[field])
        for ax in axes:
            if field == "km_travelled_per_car":
                ax.set_ylim(0, 450)
            elif field == "mean_waiting_time":
                ax.set_ylim(0, 350)
            elif not "%" in prettify(field):
                ax.set_ylim(min_val - 0.1 * max_val, 1.1 * max_val)
            else:
                ax.set_ylim(0, 1)
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
    make_avg_plots(df, "comp_times")


@print_here()
def make_comp_times_plot(df, wt, day):
    plt.figure()
    df_small = df.query("waiting_time == {} and day == {}".format(wt, day))
    ax = sns.pointplot(x="vehicles", y="comp_time", hue="capacity",
                       data=df_small, palette=clrs)
    ax.set_xticklabels(vehicles)
    ax.set_xlabel("Number of Vehicles")
    ax.set_ylabel("Computational Time [s]")
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
        title="Capacity", markerscale=3)
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
    ax.set_ylabel("Mean Computational Time [s]")
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
        title="Capacity", markerscale=3)
    filename = "figs/comp-time-w{}.png".format(wt)
    plt.savefig(filename, bbox_inches='tight')
    plt.close()


def make_interval_df():
    dfs = list()
    for i in intervals:
        df = common.get_interval_metrics(i)
        df["n_shared_per_passenger"] = df["n_shared"].sum() \
            / df["n_pickups"].sum()
        ser = df[fields + ["n_shared_per_passenger"]].mean()
        ser["km_travelled_per_car"] = df["km_travelled_per_car"].max()
        data = ser.values.reshape((1, 15))
        mean_df = pd.DataFrame(data=data, columns=ser.index)
        mean_df["interval"] = i
        dfs.append(mean_df)
    big_d = pd.concat(dfs)
    return big_d


def make_interval_plots(df):
    for field in tqdm(fields + ["n_shared_per_passenger"]):
        fig, ax = plt.subplots(1, 1, figsize=aux_fig_size)
        ax = sns.pointplot(x="interval", y=field, data=df,
                           color=sns.xkcd_rgb["bright red"], ax=ax)
        filename = "figs/interval-{}.png".format(field)
        ax.set_xlabel("Step Size [s]")
        ax.set_ylabel(prettify(field))
        if "%" in prettify(field):
            ax.set_ylim(0, 1)
            vals = ax.get_yticks()
            yticklabels = ['{:3.0f}%'.format(x * 100) for x in vals]
            ax.set_yticklabels(yticklabels)

        plt.savefig(filename, bbox_inches="tight")
        plt.close()


def make_interval_comp_plots(df):
    fig, ax = plt.subplots(1, 1, figsize=aux_fig_size)
    sns.pointplot(x="interval", y="comp_time", data=df, ax=ax,
                  color=sns.xkcd_rgb["bright red"])
    ax.set_xlabel("Step Size [s]")
    ax.set_ylabel(prettify("comp_time"))
    ax.set_xticklabels(intervals)
    plt.savefig("figs/interval-comp_time.png", bbox_inches="tight")
    plt.close()


def make_demand_df():
    dfs = list()
    for cap in [1, 4]:
        for i in demands:
            df = common.get_demand_metrics(i, cap)
            df["n_shared_per_passenger"] = df["n_shared"].sum() \
                / df["n_pickups"].sum()
            ser = df[fields + ["n_shared_per_passenger"]].mean()
            ser["km_travelled_per_car"] = df["km_travelled_per_car"].max()
            data = ser.values.reshape((1, 15))
            mean_df = pd.DataFrame(data=data, columns=ser.index)
            mean_df["demand"] = i
            mean_df["capacity"] = cap
            dfs.append(mean_df)
    big_d = pd.concat(dfs)
    return big_d


def make_demand_plots(df):
    for field in tqdm(fields + ["n_shared_per_passenger"]):
        fig, ax = plt.subplots(1, 1, figsize=aux_fig_size)
        ax = sns.pointplot(x="demand", y=field, hue="capacity", data=df,
                           palette=dem_clrs, ax=ax)
        ax.set_xlabel("Nominal Number of Requests")
        ax.set_ylabel(prettify(field))
        ax.set_xticklabels(["x0.5", "x1", "x2"])
        if "%" in prettify(field):
            ax.set_ylim(0, 1)
            vals = ax.get_yticks()
            yticklabels = ['{:3.0f}%'.format(x * 100) for x in vals]
            ax.set_yticklabels(yticklabels)
        handles, _ = ax.get_legend_handles_labels()
        ax.legend(handles, [1, 4], title="Capacity")
        filename = "figs/demand-{}.png".format(field)
        plt.savefig(filename, bbox_inches="tight")
        plt.close()


def make_demand_comp_plots(df):
    fig, ax = plt.subplots(1, 1, figsize=aux_fig_size)
    sns.pointplot(x="demand", y="comp_time", hue="capacity", data=df, ax=ax,
                  palette=dem_clrs)
    ax.set_ylabel(prettify("comp_time"))
    ax.set_xlabel("Nominal Number of Requests")
    ax.set_xticklabels(["x0.5", "x1", "x2"])
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles, [1, 4], title="Capacity")
    plt.savefig("figs/demand-comp_time.png", bbox_inches="tight")
    plt.close()


def make_hour_df():
    dfs = list()
    for i in hours:
        df = common.get_hour_metrics(i)
        df["n_shared_per_passenger"] = df["n_shared"].sum() \
            / df["n_pickups"].sum()
        ser = df[fields + ["n_shared_per_passenger"]].mean()
        ser["km_travelled_per_car"] = df["km_travelled_per_car"].max()
        data = ser.values.reshape((1, 15))
        mean_df = pd.DataFrame(data=data, columns=ser.index)
        mean_df["hour"] = i
        dfs.append(mean_df)
    big_d = pd.concat(dfs)
    return big_d


def make_hour_plots(df):
    for field in tqdm(fields + ["n_shared_per_passenger"]):
        fig, ax = plt.subplots(1, 1, figsize=aux_fig_size)
        ax = sns.barplot(x="hour", y=field, data=df,
                           color=sns.xkcd_rgb["bright red"], ax=ax)
        filename = "figs/hour-{}.png".format(field)
        ax.set_xlabel("Time of Day used for Travel Time")
        ax.set_ylabel(prettify(field))
        ax.set_xticklabels(["Mean", "12:00", "19:00"])
        if "%" in prettify(field):
            ax.set_ylim(0, 1)
            vals = ax.get_yticks()
            yticklabels = ['{:3.0f}%'.format(x * 100) for x in vals]
            ax.set_yticklabels(yticklabels)

        plt.savefig(filename, bbox_inches="tight")
        plt.close()


def make_hour_comp_plots(df):
    fig, ax = plt.subplots(1, 1, figsize=aux_fig_size)
    sns.barplot(x="hour", y="comp_time", data=df, ax=ax,
                  color=sns.xkcd_rgb["bright red"])
    ax.set_xlabel("Time of Day used for Travel Time")
    ax.set_ylabel(prettify("comp_time"))
    ax.set_xticklabels(["Mean", "12:00", "19:00"])
    plt.savefig("figs/hour-comp_time.png", bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    sns.set_context("paper", font_scale=1)
    # sns.set_context("poster", font_scale=2)
    matplotlib.rc("font", weight="bold")
    matplotlib.rc("axes", labelweight="bold")
    matplotlib.rc("axes", titleweight="bold")

    matplotlib.rc("axes", labelsize=16)
    matplotlib.rc("axes", titlesize=18)
    matplotlib.rc("xtick", labelsize=16)
    matplotlib.rc("ytick", labelsize=16)
    matplotlib.rc("legend", fontsize=12)

    plt.ioff()
    df = make_hour_df()
    # comp_df = pd.read_csv("data/hour-times.csv")
    make_hour_plots(df)
    # make_hour_comp_plots(comp_df)
    df = make_interval_df()
    make_interval_plots(df)
    # comp_df = pd.read_csv("data/interval-times.csv")
    # make_interval_comp_plots(comp_df)
    df = make_demand_df()
    make_demand_plots(df)
    # comp_df = pd.read_csv("data/demand-times.csv")
    # make_demand_comp_plots(comp_df)

    # plt.ioff()
    # sns.set_context("poster", font_scale=2)
    # big_d = get_avg_dataframe()
    # make_avg_plots(big_d, "wts")
    # parser = argparse.ArgumentParser(
    #     description=("Creates plots plots for MOD"))
    # parser.add_argument(
    #     "--plot-type", dest="plot_type", type=str,
    #     help=("Specifies the type of plot to generate. "
    #           "The options are 'area', 'area_single_day'"
    #           ", 'avg', 'comp_times', or 'ts'"))
    # args = parser.parse_args()
    # plots = {"area": [make_all_ts_area_plots],
    #          "area_single_day": [make_all_ts_area_single_plots],
    #          "avg": [make_avg_plots_with_preds,
    #                  lambda d: make_avg_plots(d, "vecs"),
    #                  lambda d: make_avg_plots(d, "wts"),
    #                  make_empty_type_plots],
    #          "ts": [make_all_ts_plots],
    #          "comp_times": [make_all_comp_times_plots]}
    # if args.plot_type == "avg":
    #     big_d = get_avg_dataframe()
    #     for func in plots["avg"]:
    #         func(big_d)
    # else:
    #     for func in plots[args.plot_type]:
    #         func()

    # df = pd.read_csv("data/times.csv")
    # make_avg_plots(df, "comp_times")
    matplotlib.rc("axes", labelsize=12)
    matplotlib.rc("axes", titlesize=12)
    matplotlib.rc("xtick", labelsize=12)
    matplotlib.rc("ytick", labelsize=12)
    matplotlib.rc("legend", fontsize=12)

    big_d = get_avg_dataframe()
    make_avg_plots(big_d, "wts")
    #
    # matplotlib.rc("axes", labelsize=18)
    # matplotlib.rc("axes", titlesize=13)
    # matplotlib.rc("xtick", labelsize=18)
    # matplotlib.rc("ytick", labelsize=18)
    # matplotlib.rc("legend", fontsize=18)

    # for vecs in [1000, 3000]:
    #     for wt in [120, 420]:
    #         make_ts_plot(vecs, wt, 0, "mean_passengers")

    # make_all_ts_area_plots()
    # make_all_ts_area_single_plots()
    # make_ts_area_plot(1000, 1, 120, 0)
    # make_ts_area_plot_single(1000, 2, 120, 0, 1)
    # make_ts_plot(1000, 120, 0, "mean_passengers")
    # make_all_ts_plots()
