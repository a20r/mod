
# import json
from tabulate import tabulate
# from load_metrics import get_ready_folders, FolderInfo
# from progressbar import ProgressBar, ETA, Percentage, Bar
# import common
from plot_metrics import get_avg_dataframe, prettify


NFS_PATH = "/home/wallar/nfs/data/data-sim/"
# NFS_PATH = "/data/drl/mod_sim_data/data-sim/"
OUTPUT_PATH = "/home/wallar/www/table.html"
TEMPLATE_PATH = "sandbox/table_template.html"


ordered_fields = ["vehicles", "capacity", "waiting_time", "predictions",
                  "mean_waiting_time", "n_shared_per_passenger",
                  "mean_passengers", "mean_delay",
                  "n_pickups", "mean_travel_delay", "serviced_percentage",
                  "total_km_travelled", "km_travelled_per_car",
                  "empty_rebalancing", "empty_moving_to_pickup",
                  "empty_waiting", "not_empty", "active_taxis", "n_shared"]


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


def create_table():
    df = get_avg_dataframe()
    datas = df.to_dict(orient="records")
    headers = datas[0].keys()
    perm = find_permutation(ordered_fields, headers)
    datas = map(lambda v: v.values(), datas)
    datas = rearrange(datas, perm)
    datas = sorted(datas, cmp=comparator)
    ord_headers = map(prettify, ordered_fields)
    return tabulate(datas, ord_headers, tablefmt="latex")


if __name__ == "__main__":
    tab = create_table()
    """
    with open(OUTPUT_PATH, "w") as fout:
        with open(TEMPLATE_PATH) as fin:
            fout.write(fin.read() + "\n" + tab)
    """
    with open("table.tex", "w") as fout:
        fout.write(tab)
