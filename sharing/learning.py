
import csv
import io
from collections import defaultdict
from features import feature_names


class DemandProbability(object):

    def fit(self, fn_in):
        with io.open(fn_in, "rb") as fin:
            reader = csv.DictReader(fin, fieldnames=feature_names)
            num_pd = defaultdict(lambda: defaultdict(float))
            num_p = defaultdict(lambda: defaultdict(float))
            num_tau = defaultdict(float)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                t = int(float(row["p_time"]) * 24 * 4)
                p = int(row["p_station"])
                d = int(row["d_station"])
                pc = int(float(row["passenger_count"]))
                day = int(row["p_day"])
                tau = (t, day)
                num_pd[tau][(p, d)] += pc
                num_p[tau][p] += pc
                num_tau[tau] += pc
            self.num_pd = num_pd
            self.num_p = num_p
            self.num_tau = num_tau
            return self

    def __call__(self, p, d, t, day):
        tau = (t, day)
        prob_pd = self.num_pd[tau][(p, d)] / self.num_tau[tau]
        return prob_pd

    def dump(self, fn_out):
        cols = ["time", "day", "pickup", "dropoff", "probability"]
        with io.open(fn_out, "wb") as fout:
            writer = csv.writer(fout)
            writer.writerow(cols)
            for (t, day) in self.num_pd.keys():
                for (p, d) in self.num_pd[(t, day)].keys():
                    prob = self(p, d, t, day)
                    writer.writerow([t, day, p, d, prob])
        return self


if __name__ == "__main__":
    dp = DemandProbability()
    dp.fit("data/trip_data_5_features.csv")
    dp.dump("models/probs.csv")
