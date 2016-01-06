
import requests
import numpy as np


url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={}" +\
    "&destinations={}&departure_time={}&traffic_model=best_guess"


def google_list(strs):
    return "|".join(st for st in strs)


def travel_times_request(stations, departure_time):
    sts = list()
    st_str = "{},{}"
    for st in stations:
        sts.append(st_str.format(st[1], st[0]))
    gsts = google_list(sts)
    query_url = url.format(gsts, gsts, departure_time)
    return requests.get(query_url)


def travel_times(stations, departure_time):
    r = travel_times_request(stations, departure_time)
    if r.status_code == 200:
        tt = r.json()
        times = np.zeros((len(stations), len(stations)))
        for i, row in enumerate(tt["rows"]):
            for j, element in enumerate(row["elements"]):
                print element
                try:
                    times[i][j] = element["duration"]["value"]
                except:
                    print stations[i], stations[j]
        return times
