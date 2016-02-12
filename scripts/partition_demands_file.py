
import common
import time
import argparse
import csv
import io
from collections import defaultdict


df_template = "data/demands_{}_{}_{}.csv"


def partition_by_day(fn_huge, fn_filtered):
    print "Filtering file based on weekday..."
    current_day = None
    day_count = defaultdict(int)
    with io.open(fn_huge, "rb") as fin:
        with io.open(fn_filtered, "wb") as fout:
            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=common.fn_demands_fields)
            writer.writeheader()
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                row = common.clean_dict(row)
                str_time = row["pickup_datetime"]
                t = time.strptime(str_time, common.date_format)
                if t.tm_wday in wds:
                    if current_day != t.tm_yday:
                        current_day = t.tm_yday
                        if day_count[t.tm_wday] <= max_wds:
                            day_count[t.tm_wday] += 1
                        if sum(day_count.values()) > len(wds) * max_wds:
                            return
                    if day_count[t.tm_yday] <= max_wds:
                        writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Filters the CSV file to accumulate all the data for a\
        given day of the week")
    parser.add_argument(
        "--fn_demands", dest="fn_demands", type=str,
        default="data/demands.csv",
        help="CSV file containing the demands.")
    parser.add_argument(
        "--fn_filtered", dest="fn_filtered", type=str,
        default="data/data_short.csv",
        help="CSV file containing filtered data for a given day.")
    args = parser.parse_args()
    partition_by_day(args.fn_raw, args.fn_filtered, args.weekday, args.n_days)
