
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
from collections import defaultdict
from itertools import product
from table_common import table_header, line_tp, table_footer

instances = [(500, 1, 0), (500, 2, 0), (500, 3, 0), (500, 4, 0),
             (125, 4, 0), (250, 4, 0), (375, 4, 0), (625, 4, 0),
             (750, 4, 0), (1000, 4, 0), (250, 4, 1), (375, 4, 1),
             (500, 4, 1), (625, 4, 1), (750, 4, 1)]


n_vecs = [125, 250, 375, 500, 625, 750, 1000]
predictions = [0, 100, 200, 300, 400]
waiting_times = [120, 300, 420]
vehicles = [1000, 2000, 3000]
fields = ["mean_waiting_time", "mean_passengers", "mean_delay", "n_pickups",
          "mean_travel_delay", "serviced_percentage", "total_km_travelled",
          "km_travelled_per_car"]
caps = [1, 2, 4, 10]
clrs = ["ro", "go", "bo", "co", "mo"]


def prettify(text):
    if text == "n_pickups":
        return "Num Pickups"
    else:
        words = text.split("_")
        return " ".join(w.capitalize() for w in words)


def make_wt_title(field, nvs):
    return "{} w/ N.V: {}, {}, {}".format(prettify(field), *nvs)


def make_vec_title(field, wts):
    return "{} w/ M.W.T: {}, {}, {}".format(prettify(field), *wts)


def make_pred_title(field, wt, cap):
    return "{} w/ M.W.T: {} | Cap: {}".format(prettify(field), wt, cap)


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


def plot_ts(df, field, *args, **kwargs):
    dates = df["time"]
    values = df[field]
    dts = list()
    for i in xrange(len(dates)):
        dt = datetime.strptime(dates.iloc[i], common.date_format)
        dts.append(dt)
    dts = matplotlib.dates.date2num(dts)
    plt.plot_date(dts, values, *args, **kwargs)


def make_ts_plots():
    fmt = DateFormatter("%m/%d")
    for field in fields:
        for v in vehicles:
            for wt in waiting_times:
                fig, ax = plt.subplots()
                for cap, clr in zip(caps, clrs):
                    df = tabler.get_metrics(v, cap, wt, 0)
                    plot_ts(df, field, clr, alpha=0.8,
                            label="Cap: {}".format(cap))
                ax.xaxis.set_major_formatter(fmt)
                lgd = plt.legend(loc="center left", fancybox=True,
                                 shadow=True, bbox_to_anchor=(1, 0.5))
                plt.ylabel(field)
                fig.autofmt_xdate()
                plt.savefig("figs/ts-{}-v{}-w{}.pdf".format(field, v, wt),
                            bbox_extra_artists=(lgd,), bbox_inches='tight')


def get_avg_dataframe():
    cols=["predictions", "vehicles", "waiting_time", "capacity"] + fields \
        + map(lambda f: f + "_std", fields)
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
            data.loc[counter] = [p, v, wt, cap] + f_vals + f_stds
            counter += 1
        except IOError:
            pass
    return data


def make_avg_plots_with_preds(big_d):
    d = big_d.query("capacity == 4 and waiting_time == 300")
    cap, wt = 4, 300
    for field in fields:
        ax = sns.pointplot(x="vehicles", y=field, hue="predictions", data=d)
        plt.ylabel(prettify(field))
        plt.xlabel("Num Vehicles")
        lgd = plt.legend(
            loc="center left", fancybox=True,
            shadow=True, bbox_to_anchor=(1, 0.5),
            title="Predictions")
        plt.title(make_pred_title(field, wt, cap))
        plt.savefig(
            "figs/avg-with-preds-{}.pdf".format(field),
            bbox_inches='tight')
        plt.close()


def make_avg_plots_with_vecs(big_d):
    for field in fields:
        max_val = None
        min_val = None
        axes = list()
        for i, wt in enumerate(waiting_times, start=1):
            plt.subplot(1, len(waiting_times), i)
            q = "predictions == 0 and waiting_time == {}".format(wt)
            d = big_d.query(q)
            ax = sns.pointplot(x="vehicles", y=field, hue="capacity", data=d)
            ax.grid("on")
            axes.append(ax)
            ax.legend().remove()
            if i == 1:
                plt.ylabel(prettify(field))
            else:
                plt.ylabel("")
            if i == 2:
                plt.xlabel("Number of Vehicles")
                plt.title(make_vec_title(field, waiting_times))
            else:
                plt.xlabel("")
            if i > 1:
                ax.get_yaxis().set_ticklabels([])
            if i == len(waiting_times):
                lgd = plt.legend(
                    loc="center left", fancybox=True,
                    shadow=True, bbox_to_anchor=(1, 0.5),
                    title="Capacities")
            if max_val is None or max_val < max(d[field]):
                max_val = max(d[field])
            if min_val is None or min_val > min(d[field]):
                min_val = min(d[field])
        for ax in axes:
            ax.set_ylim(min_val - 0.1 * max_val, 1.1 * max_val)
        filename = "figs/avg-with-vecs-{}.pdf".format(field)
        plt.savefig(filename, bbox_inches='tight')
        plt.close()


def make_avg_plots_with_wts(big_d):
    for field in fields:
        max_val = None
        min_val = None
        axes = list()
        for i, v in enumerate(vehicles, start=1):
            plt.subplot(1, len(vehicles), i)
            q = "predictions == 0 and vehicles == {}".format(v)
            d = big_d.query(q)
            ax = sns.pointplot(x="waiting_time", y=field, hue="capacity",
                               data=d)
            ax.grid("on")
            axes.append(ax)
            ax.legend().remove()
            if i == 1:
                plt.ylabel(prettify(field))
            else:
                plt.ylabel("")
            if i == 2:
                plt.xlabel("Max Waiting Time")
                plt.title(make_wt_title(field, vehicles))
            else:
                plt.xlabel("")
            if i > 1:
                ax.get_yaxis().set_ticklabels([])
            if i == len(waiting_times):
                lgd = plt.legend(
                    loc="center left", fancybox=True,
                    shadow=True, bbox_to_anchor=(1, 0.5),
                    title="Capacities")
            if max_val is None or max_val < max(d[field]):
                max_val = max(d[field])
            if min_val is None or min_val > min(d[field]):
                min_val = min(d[field])
        for ax in axes:
            ax.set_ylim(min_val - 0.1 * max_val, 1.1 * max_val)
        filename = "figs/avg-with-wts-{}.pdf".format(field)
        plt.savefig(filename, bbox_inches='tight')
        plt.close()


if __name__ == "__main__":
    plt.ioff()
    sns.set_context("poster", font_scale=1.7)
    big_d = get_avg_dataframe()
    make_avg_plots_with_preds(big_d)
    make_avg_plots_with_wts(big_d)
    make_avg_plots_with_vecs(big_d)
    make_ts_plots()
