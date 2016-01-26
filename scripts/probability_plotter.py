
import argparse


def plot_probabilities(fn_probs, interval, weekday):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot the probability of a given requests.")
    parser.add_argument(
        "--fn_probs", dest="fn_probs", type=str,
        default="data/probs.csv",
        help="CSV of probabilities for given requests.")
    parser.add_argument(
        "--interval", dest="interval", type=int, default=0,
        help="Interval for pickup probabilities.")
    parser.add_argument(
        "--weekday", dest="weekday", type=int, default=0,
        help="Day of the week for pickup probabilities.")
    args = parser.parse_args()
    plot_probabilities(args.fn_probs, args.interval, args.weekday)
