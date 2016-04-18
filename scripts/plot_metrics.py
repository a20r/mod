
import common
import numpy as np
import seaborn as sns
import pandas
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
from table_common import table_header, line_tp, table_footer

instances = [(500, 1, 0), (500, 2, 0), (500, 3, 0), (500, 4, 0),
             (125, 4, 0), (250, 4, 0), (375, 4, 0), (625, 4, 0),
             (750, 4, 0), (1000, 4, 0), (250, 4, 1), (375, 4, 1),
             (500, 4, 1), (625, 4, 1), (750, 4, 1)]


n_vecs = [125, 250, 375, 500, 625, 750, 1000]


def create_latex_table(df):
    lines = list()
    for i, (n_vecs, cap, rb) in enumerate(instances):
        st = subtable(df, n_vecs, cap, rb)
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


def subtable(df, n_vecs, cap, rebalancing=0, is_long=0):
    bcap = (df["capacity"] == cap)
    bvecs = (df["n_vehicles"] == n_vecs)
    brb = (df["rebalancing"] == rebalancing)
    isl = (df["is_long"] == is_long)
    return df[bcap & bvecs & brb & isl]


def plot_date(dates, values, *args, **kwargs):
    dts = list()
    for i in xrange(len(dates)):
        dt = datetime.strptime(dates.iloc[i], common.date_format)
        dts.append(dt)
    dts = matplotlib.dates.date2num(dts)
    plt.plot_date(dts, values, *args, **kwargs)


def plot_percent_pickups_vs_vehicles(df):
    plt.figure()
    ys = list()
    for n_vec in n_vecs:
        st = subtable(df, n_vec, 4)
        try:
            picked = float(np.sum(st["n_pickups"]))
            ignored = float(np.sum(st["n_ignored"]))
            ys.append(100 * picked / (picked + ignored))
        except ZeroDivisionError:
            ys.append(0)
    sns.barplot(x=np.array(n_vecs), y=np.array(ys))
    plt.xlabel("Number of Vehicles")
    plt.ylabel("Picked Requests [%]")


def plot_pickups_vs_time(df):
    fig = plt.figure()
    st = subtable(df, 1000, 10, 1, 1)
    plot_date(st["time"], st["n_pickups"], "ro", alpha=1)
    plt.xlabel("Time")
    plt.ylabel("Number of Pickups per 30s Segment")
    fig.autofmt_xdate()


def plot_occupancy(df):
    plt.figure()
    st = subtable(df, 500, 4, 0, 1)
    start = datetime.strptime(st["time"].loc[6024], common.date_format)
    end = datetime.strptime(st["time"].loc[8902], common.date_format)
    st.index = pandas.date_range(start, end, freq="30S")
    ys = st["mean_passengers"]
    plt.plot(st.index, ys, "r")
    stds = st["std_passengers"]
    plt.fill_between(st.index, ys - stds, ys + stds, color="r", alpha=0.2)
    plt.xlabel("Time")
    plt.ylabel("Average Occupancy Per Vehicle")
    plt.ylim([0, 4])
    plt.yticks(range(5))


if __name__ == "__main__":
    sns.set_context("poster", font_scale=2.2)
    m_file = "/home/wallar/nfs/data/data-sim/v1000-c10-w120-p0/metrics.csv"
    df = pandas.read_csv(m_file)
    # table = create_latex_table(df)
    # print table
    # plot_occupancy(df)
    # plot_percent_pickups_vs_vehicles(df)
    plot_pickups_vs_time(df)
    # plt.fill_between(ma.index, ma - mstd, ma + mstd, color="r", alpha=0.4)
    plt.show()
