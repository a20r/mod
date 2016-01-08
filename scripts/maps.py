
import requests
import math
import numpy as np


url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={}" +\
    "&destinations={}&key=AIzaSyDrLbHeoPOYRcAnagqQHTElT905Jov1oec"
origin = "{},{}"

n_dest = 35


def geo_dist(p1, p2):
    lat1 = p1[1]
    lon1 = p1[0]
    lat2 = p2[1]
    lon2 = p2[0]
    lon1 = lon1 * (math.pi / 180.0)
    lat1 = lat1 * (math.pi / 180.0)
    lon2 = lon2 * (math.pi / 180.0)
    lat2 = lat2 * (math.pi / 180.0)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = pow(math.sin(dlat / 2.0), 2) + math.cos(lat1) * \
        math.cos(lat2) * pow(math.sin(dlon / 2.0), 2)
    c = 2 * math.asin(math.sqrt(a))
    dist_km = 6367 * c
    return dist_km


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


def travel_times_gmaps(stations):
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


def travel_times(stations):
    times = np.zeros((len(stations), len(stations)))
    for i, m in enumerate(stations):
        for j, n in enumerate(stations):
            times[i][j] = geo_dist(m, n)
    return times


def travel_times_gmaps_old(stations):
    r = travel_times_request(stations)
    if r.status_code == 200:
        tt = r.json()
        times = np.zeros((len(stations), len(stations)))
        for i, row in enumerate(tt["rows"]):
            for j, element in enumerate(row["elements"]):
                times[i][j] = element["duration"]["value"]
        return times
