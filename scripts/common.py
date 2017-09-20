
import re
import pandas as pd
import time
import shapely.geometry as geom


NFS_PATH = "/home/wallar/nfs/data/data-sim/"
# ]]NFS_PATH = "/data/drl/mod_sim_data/data-sim/"


def get_metrics(n_vehicles, cap, waiting_time, predictions):
    m_file = NFS_PATH + "v{}-c{}-w{}-p{}/metrics_pnas.csv".format(
        n_vehicles, cap, waiting_time, predictions)
    df = pd.read_csv(m_file)
    df.sort_values("time", inplace=True)
    df.reset_index(inplace=True)
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


def get_interval_metrics(interval):
    if interval == 30:
        return get_metrics(2000, 4, 300, 0)

    m_file = NFS_PATH + "v{}-c{}-w{}-p{}-i{}/metrics_pnas.csv".format(
        2000, 4, 300, 0, interval)
    df = pd.read_csv(m_file)
    df.sort_values("time", inplace=True)
    df.reset_index(inplace=True)
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


def get_demand_metrics(demand, cap=4):
    if demand == "same":
        return get_metrics(2000, cap, 300, 0)
    if cap == 1:
        if demand == "half":
            demand = "short"
        if demand == "double":
            demand = "long"

    m_file = NFS_PATH + "v{}-c{}-w{}-p{}-{}/metrics_pnas.csv".format(
        2000, cap, 300, 0, demand)
    df = pd.read_csv(m_file)
    df.sort_values("time", inplace=True)
    df.reset_index(inplace=True)
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


def get_hour_metrics(hour, cap=4):
    if hour == "same":
        return get_metrics(2000, cap, 300, 0)

    m_file = NFS_PATH + "v{}-c{}-w{}-p{}-{}/metrics_pnas.csv".format(
        2000, cap, 300, 0, hour)
    df = pd.read_csv(m_file)
    df.sort_values("time", inplace=True)
    df.reset_index(inplace=True)
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


def load_kml_poly():
    try:
        with open("data/nyc.kml") as fin:
            data = fin.read()
            cs = re.findall(r"<coordinates>[\s\S]*?<\/coordinates>", data)[0] \
                .split("<coordinates>")[1]\
                .split(",0 ")[:-2]
            poly = list()
            for gs in cs:
                coords = map(float, gs.strip().split(","))
                poly.append(coords)
            return poly
    except:
        return []


MAX_SECONDS = 60240

date_format = "%Y-%m-%d %H:%M:%S"

# nyc_poly = [[-74.01824376474143, 40.73320343981938],
#             [-73.97199182307409, 40.73326660593117],
#             [-73.96899528222204, 40.74472418510373],
#             [-73.94812921425887, 40.77053734232472],
#             [-73.99885640649616, 40.77082617894838]]

nyc_poly = load_kml_poly()
geom_nyc_poly = None

fl_huge = 15285050

fn_raw_fields = ["medallion", "hack_license", "vendor_id", "rate_code",
                 "store_and_fwd_flag", "pickup_datetime", "dropoff_datetime",
                 "passenger_count", "trip_time_in_secs", "trip_distance",
                 "pickup_longitude", "pickup_latitude", "dropoff_longitude",
                 "dropoff_latitude"]

fn_stations_fields = ["id", "latitude", "longitude"]

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def convert_date_to_interval(str_time, interval):
    t = time.strptime(str_time, DATE_FORMAT)
    secs = t.tm_hour * 60 * 60 + t.tm_min * 60 + t.tm_sec
    return secs / (interval * 60), t.tm_wday


def get_nyc_poly():
    global geom_nyc_poly
    if geom_nyc_poly is None:
        with open("data/nyc.kml") as fin:
            data = fin.read()
            cs = re.findall(r"<coordinates>[\s\S]*?<\/coordinates>", data)[0] \
                .split("<coordinates>")[1]\
                .split(",0 ")[:-2]
            poly = list()
            for gs in cs:
                coords = map(float, gs.strip().split(","))
                poly.append(coords)
            geom_nyc_poly = geom.Polygon(poly)
    return geom_nyc_poly


def within_region(lons, lats):
    nyc = get_nyc_poly()
    bools = list()
    for lon, lat in zip(lons, lats):
        bools.append(nyc.contains(geom.Point(lon, lat)))
    return bools


def clean_df(df):
    df.rename(columns=lambda x: x.strip(), inplace=True)
    d_qstr = "dropoff_latitude != 0 and dropoff_longitude != 0"
    p_qstr = "pickup_latitude != 0 and pickup_longitude != 0"
    df.query(d_qstr, inplace=True)
    df.query(p_qstr, inplace=True)
    df = df[within_region(df["pickup_longitude"], df["pickup_latitude"])]
    df = df[within_region(df["dropoff_longitude"], df["dropoff_latitude"])]
    return df


def clean_dict(val_dict):
    clean = dict()
    for key in val_dict.keys():
        k = key.strip()
        try:
            clean[k] = float(val_dict[key])
        except:
            clean[k] = val_dict[key]
    return clean


def load_data(fn_raw, chunksize):
    dfs = pd.read_csv(fn_raw, parse_dates=True, infer_datetime_format=True,
                      chunksize=chunksize, engine="python")
    return dfs
