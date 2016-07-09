
import pandas
import json
from tabulate import tabulate
from load_metrics import get_ready_folders, FolderInfo
from progressbar import ProgressBar, ETA, Percentage, Bar


NFS_PATH = "/home/wallar/nfs/data/data-sim/"
OUTPUT_PATH = "/home/wallar/www/table.html"
TEMPLATE_PATH = "sandbox/table_template.html"


def get_metrics(n_vehicles, cap, waiting_time, predictions):
    m_file = NFS_PATH + "v{}-c{}-w{}-p{}/metrics_even_newerest.csv".format(
        n_vehicles, cap, waiting_time, predictions)
    df = pandas.read_csv(m_file)
    df = df.query("time.hour > 0")
    df["serviced_percentage"] = df["n_pickups"].sum() \
        / (df["n_pickups"].sum() + df["n_ignored"].sum())
    df["mean_travel_delay"] = df["mean_delay"] - df["mean_waiting_time"]
    df["serviced_percentage"] = df["n_pickups"].sum() / \
        (df["n_ignored"].sum() + df["n_pickups"].sum())
    df["km_travelled_per_car"] = df["total_km_travelled"] / df["n_vehicles"]
    df["n_shared_perc"] = df["n_shared"] / (df["n_shared"] + df["time_pass_1"])
    df.drop("Unnamed: 0", axis=1, inplace=True)
    df.drop("capacity", axis=1, inplace=True)
    df.drop("is_long", axis=1, inplace=True)
    df.drop("n_vehicles", axis=1, inplace=True)
    return df


def avg_cols(df):
    return df.mean(numeric_only=True)


def comparator(A, B):
    for i in xrange(len(A)):
        if A[i] < B[i]:
            return -1
        if A[i] > B[i]:
            return 1
    return 0


def create_table(table_filename):
    dirs = get_ready_folders(NFS_PATH)
    datas = list()
    preface = "Creating Table: "
    widgets = [preface, Bar(), Percentage(), "| ", ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=len(dirs)).start()
    headers = None
    for i, dr in enumerate(dirs):
        try:
            info = FolderInfo(dr)
            metrics = get_metrics(
                info.n_vehicles, info.max_capacity,
                info.max_waiting_time, info.predictions)
            avg_metrics = avg_cols(metrics).to_dict()
            datas.append(info.to_dict().values()
                         + avg_metrics.values())
            if headers is None:
                headers = info.to_dict().keys() + avg_metrics.keys()
        except IOError:
            pass
        pbar.update(i + 1)
    pbar.finish()
    with open(table_filename, "w") as f:
        json.dump(datas, f)
    datas = sorted(datas, cmp=comparator)
    return tabulate(datas, headers, tablefmt="html")


if __name__ == "__main__":
    tab = create_table("/home/wallar/nfs/data/table.json")
    with open(OUTPUT_PATH, "w") as fout:
        with open(TEMPLATE_PATH) as fin:
            fout.write(fin.read() + "\n" + tab)
