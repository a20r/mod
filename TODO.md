# Things that need doing

- [x] For a day: save in .txt all the requests with origin and
destination, like the demands.txt attached. Also store in another file
the # taxis.

- [x] Compute N stations (N=100 initially, later N=1000) and store them in
two files, one with positions and the other one with travel times,
like distances.txt and stationLUT.txt

- [ ] In C++, function that given a position p = (lat,lon) and a station K
outputs the approximate travel time p->K given by: V *
dist(p,closest_station) + travel_time(closest station, p), where
closest_station is queried from KD-tree.

- [x] Compute from several days the predicted requests (origin ->
destination) for 15 minutes intervals of a day. Store it in a file.

- [x] In C++, function that given (N, time) outputs N sampled requests
from the distribution above.

- [x] Determine the expected number of requests for a given time interval

- [ ] Record the expected number of requests in a day

- [x] Determine the number of taxis and save to file or something like that

## Next
A visualization, given all the requests, positions of the
vehicles, pickups and dropoffs through out a day, visualize them on
top of a map.

