
import numpy as np
from progressbar import ProgressBar, ETA, Percentage, Bar
import pickle


def load_path(path_str):
    path = map(int, path_str.split(" "))
    return path[0], path[1], path[2:]


def check_times(fn_times, fn_paths):
    times = np.loadtxt(fn_times, skiprows=1)
    pbar = ProgressBar(
        widgets=["Debugging Paths File: ", Bar(), Percentage(), "|", ETA()],
        maxval=pow(times.shape[0], 2)).start()
    not_close = list()
    counter = 1
    with open(fn_paths, "rb") as fin:
        for line in fin:
            st, end, path = load_path(line)
            est_time = times[st][end]
            total_time = 0
            if len(path) > 1:
                for i in xrange(len(path) - 1):
                    total_time += times[path[i]][path[i + 1]]
            isc = np.isclose(total_time, est_time)
            if not isc:
                data = dict()
                data["start"] = st
                data["end"] = end
                data["est_time"] = est_time
                data["total_time"] = total_time
                data["path"] = path
                not_close.append(data)
            pbar.update(counter)
            counter += 1
    pbar.finish()
    print "Writing to file"
    with open("data/times_debug.pickle", "wb") as fout:
        pickle.dump(not_close, fout)


if __name__ == "__main__":
    check_times("data/times.csv", "data/paths.csv")
