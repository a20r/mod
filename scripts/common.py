
import re


def load_kml_poly():
    with open("data/nyc.kml") as fin:
        data = fin.read()
        cs = re.findall(r"<coordinates>[\s\S]*?<\/coordinates>", data)[0]\
            .split("<coordinates>")[1]\
            .split(",0 ")[:-2]
        poly = list()
        for gs in cs:
            coords = map(float, gs.strip().split(","))
            poly.append(coords)
        return poly


MAX_SECONDS = 60240

date_format = "%Y-%m-%d %H:%M:%S"

# nyc_poly = [[-74.01824376474143, 40.73320343981938],
#             [-73.97199182307409, 40.73326660593117],
#             [-73.96899528222204, 40.74472418510373],
#             [-73.94812921425887, 40.77053734232472],
#             [-73.99885640649616, 40.77082617894838]]

nyc_poly = load_kml_poly()

fl_huge = 15285050

fn_raw_fields = ["medallion", "hack_license", "vendor_id", "rate_code",
                 "store_and_fwd_flag", "pickup_datetime", "dropoff_datetime",
                 "passenger_count", "trip_time_in_secs", "trip_distance",
                 "pickup_longitude", "pickup_latitude", "dropoff_longitude",
                 "dropoff_latitude"]

fn_stations_fields = ["id", "latitude", "longitude"]


def clean_dict(val_dict):
    clean = dict()
    for key in val_dict.keys():
        k = key.strip()
        try:
            clean[k] = float(val_dict[key])
        except:
            clean[k] = val_dict[key]
    return clean
