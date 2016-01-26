
import common
import argparse
from progressbar import ProgressBar, ETA, Percentage, Bar


def filter_data_for_day(fn_huge, fn_filtered, wd, max_wds=1):
    pbar = ProgressBar(
        widgets=["Filtering File: ", Bar(), Percentage(), "|", ETA()],
        maxval=fl + 1).start()
    with io.open(fn_huge, "rb") as f_in:
        with io.open(fn_filtered, "wb") as fout:
            reader = csv.DictReader(fin)
            writer = csv.writer(fout)
            for i, row in enumerate(reader):
                if i == 0:
                    writer.writerow(row)
                else:
                    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Filters the CSV file to accumulate all the data for a\
        given day of the week")
    parser.add_argument(
        "--fn_raw", dest="fn_raw", type=str,
        default="data/trip_data_5.csv",
        help="CSV file containing the raw NY taxi data.")
    parser.add_argument(
        "--fn_filtered", dest="fn_filtered", type=str,
        default="data/data_short.csv",
        help="CSV file containing filtered data for a given day.")
    parser.add_argument(
        "--weekday", dest="weekday", type=int, default=4,
        help="Day of the week to gather data.")
    args = parser.parse_args()
    filter_data_for_day(args.fn_raw, args.fn_filtered, args.weekday)
