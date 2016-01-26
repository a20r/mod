
date_format = "%Y-%m-%d %H:%M:%S"

nyc_rect = (-73.993498, 40.752273, -73.957058, 40.766382)

nyc_poly = [[-74.00581013056571, 40.74079128485756],
            [-73.98443319243493, 40.73201598875866],
            [-73.96720621583611, 40.76092244997941],
            [-73.98949052917897, 40.76957871013592]]
fl_huge = 15285050

fn_raw_fields = ["medallion", "hack_license", "vendor_id", "rate_code",
                 "store_and_fwd_flag", "pickup_datetime", "dropoff_datetime",
                 "passenger_count", "trip_time_in_secs", "trip_distance",
                 "pickup_longitude", "pickup_latitude", "dropoff_longitude",
                 "dropoff_latitude"]


def clean_dict(val_dict):
    clean = dict()
    for key in val_dict.keys():
        k = key.strip()
        try:
            clean[k] = float(val_dict[key])
        except:
            clean[k] = val_dict[key]
    return clean

