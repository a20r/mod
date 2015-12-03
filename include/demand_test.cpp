
#include <iostream>
#include "demand.hpp"

using namespace std;

int main() {
    GeoLocation p_st(-73.991788392187516, -73.991788392187516);
    GeoLocation d_st(-73.78195999999997,-73.78195999999997);
    DemandLookup dl("../data/trip_data_5_stations_short.csv",
            "../data/trip_data_5_probs_short.csv");
    cout << dl.query_demand(0, 2, p_st, d_st) << endl;
}
