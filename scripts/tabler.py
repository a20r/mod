
import pandas as pd
from tabulate import tabulate
from plot_metrics import get_avg_dataframe, prettify


# NFS_PATH = "/home/wallar/nfs/data/data-sim/"
NFS_PATH = "/data/drl/mod_sim_data/data-sim/"
OUTPUT_PATH = "/home/wallar/www/{}.html"
TEMPLATE_PATH = "sandbox/table_template.html"


# ordered_fields = ["vehicles", "capacity", "waiting_time", "predictions",
#                   "mean_waiting_time", "n_shared_per_passenger",
#                   "mean_passengers", "mean_delay",
#                   "n_pickups", "mean_travel_delay", "serviced_percentage",
#                   "total_km_travelled", "km_travelled_per_car",
#                   "empty_rebalancing", "empty_moving_to_pickup",
#                   "empty_waiting", "not_empty", "active_taxis", "n_shared"]

ordered_fields = ["vehicles", "capacity", "waiting_time",
                     "serviced_percentage", "mean_waiting_time",
                     "mean_travel_delay", "mean_passengers", 
                    "n_shared_per_passenger", "km_travelled_per_car",
                    "predictions", "n_pickups", "mean_delay", "total_km_travelled",
                    "empty_rebalancing", "empty_moving_to_pickup",
                    "empty_waiting", "not_empty", "active_taxis", "n_shared"]

ct_fields = ["vehicles", "capacity", "waiting_time", "comp_time"]


def avg_cols(df):
    return df.mean(numeric_only=True)


def comparator(A, B):
    for i in xrange(len(A)):
        if A[i] < B[i]:
            return -1
        if A[i] > B[i]:
            return 1
    return 0


def rearrange(datas, perm):
    new_datas = list()
    for row in datas:
        new_row = [0] * len(row)
        for i, val in enumerate(row):
            new_row[perm[i]] = val
        new_datas.append(new_row)
    return new_datas


def find_permutation(control, alternate):
    """ Returns a mapping from alternate to control """
    reverse_dict = dict()
    perm = [0] * len(control)
    for i, val in enumerate(alternate):
        reverse_dict[val] = i
    for i, val in enumerate(control):
        perm[reverse_dict[val]] = i
    return perm


def create_table(df, ord_fields, tablefmt):
    datas = df.to_dict(orient="records")
    headers = datas[0].keys()
    perm = find_permutation(ord_fields, headers)
    datas = map(lambda v: v.values(), datas)
    datas = rearrange(datas, perm)
    datas = sorted(datas, cmp=comparator)
    ord_headers = map(prettify, ord_fields)
    return tabulate(datas, ord_headers, tablefmt=tablefmt)


if __name__ == "__main__":
    df = get_avg_dataframe()
    # tab = create_table(df, ordered_fields, "html")
    # with open(OUTPUT_PATH.format("table"), "w") as fout:
    #     with open(TEMPLATE_PATH) as fin:
    #         fout.write(fin.read() + "\n" + tab)
    tab = create_table(df, ordered_fields, "latex")
    with open("table.tex", "w") as fout:
        fout.write(tab)
    ct_df = pd.read_csv("data/times.csv")
    ct_df.drop("Unnamed: 0", axis=1, inplace=True)
    ct_df = ct_df.groupby(["vehicles", "capacity", "waiting_time"]).mean()
    ct_df.drop("day", axis=1, inplace=True)
    ct_df.reset_index(inplace=True)
    tab = create_table(ct_df, ct_fields, "latex")
    with open("comp_times_table.tex", "w") as fout:
        fout.write(tab)
    # tab = create_table(ct_df, ct_fields, "html")
    # with open(OUTPUT_PATH.format("comp_times"), "w") as fout:
    #     with open(TEMPLATE_PATH) as fin:
    #         fout.write(fin.read() + "\n" + tab)
