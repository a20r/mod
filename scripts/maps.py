
import requests
import numpy as np


url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={}" +\
    "&destinations={}&key=AIzaSyDrLbHeoPOYRcAnagqQHTElT905Jov1oec"
origin = "{},{}"

n_dest = 35


def google_list(strs):
    return "|".join(st for st in strs)


def travel_times_request(current, stations):
    sts = list()
    st_str = "{},{}"
    for st in stations:
        sts.append(st_str.format(st[1], st[0]))
    gsts = google_list(sts)
    ori = origin.format(st[1], st[0])
    query_url = url.format(ori, gsts)
    return requests.get(query_url)


def travel_times_requests(stations):
    n_req = len(stations) / n_dest
    reqs = [list()] * len(stations)
    for i, st in enumerate(stations):
        for j in xrange(n_req):
            sts = stations[j * n_dest:n_dest * (j + 1)]
            r = travel_times_request(st, sts)
            reqs[i].append(r)
        sts = stations[n_req * n_dest:]
        r = travel_times_request(st, sts)
        reqs[i].append(r)
    return reqs


def travel_times(stations):
    reqs = travel_times_requests(stations)
    times = np.zeros((len(stations), len(stations)))
    for i, st_reqs in enumerate(reqs):
        j = 0
        for req in st_reqs:
            print req.text
            tt = req.json()
            for element in tt["rows"][0]["elements"]:
                times[i][j] = element["duration"]["value"]
                j += 1
    return times


def travel_times_old(stations):
    r = travel_times_request(stations)
    if r.status_code == 200:
        tt = r.json()
        times = np.zeros((len(stations), len(stations)))
        for i, row in enumerate(tt["rows"]):
            for j, element in enumerate(row["elements"]):
                times[i][j] = element["duration"]["value"]
        return times
