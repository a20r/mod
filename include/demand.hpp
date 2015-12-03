
#ifndef DEMAND_HPP
#define DEMAND_HPP

#include <sstream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <functional>

using namespace std;

class GeoLocation {
    public:
        double lon, lat;
        GeoLocation() {};
        ~GeoLocation() {};
        GeoLocation(double lon, double lat) : lon(lon), lat(lat) {};
};

class Demand {
    public:
        int time, day, pickup, dropoff;

        Demand() {};

        Demand(int time, int day, int pickup, int dropoff) {
            this->time = time;
            this->day = day;
            this->pickup = pickup;
            this->dropoff = dropoff;
        }
};

class DemandHash {
    public:
        size_t operator() (const Demand& demand) const {
            stringstream buffer;
            buffer << demand.time << " ";
            buffer << demand.day << " ";
            buffer << demand.pickup << " ";
            buffer << demand.dropoff;
            return hash<string>()(buffer.str());
        }
};

inline bool operator== (Demand const& lhs, Demand const& rhs) {
    return lhs.time == rhs.time and lhs.day == rhs.day and
        lhs.pickup == rhs.pickup and lhs.dropoff == rhs.dropoff;
};

class DemandLookup {

    private:
        unordered_map<Demand, double, DemandHash> demands;

    public:
        DemandLookup() {};
        ~DemandLookup() {};

        DemandLookup(string prob_fn, string feat_fn) {
            int time, day, pickup, dropoff;
            double prob;

            ifstream data(prob_fn);
            string line;

            getline(data, line);
            while(getline(data, line)) {
                stringstream lineStream(line);
                string cell;
                int counter = 0;
                while(std::getline(lineStream, cell, ',')) {
                    switch (counter++) {
                        case 0:
                            time = stoi(cell);
                            break;
                        case 1:
                            day = stoi(cell);
                            break;
                        case 2:
                            pickup = stoi(cell);
                            break;
                        case 3:
                            dropoff = stoi(cell);
                            break;
                        case 4:
                            prob = stof(cell);
                            break;
                        default:
                            break;
                    }
                }
                Demand dem(time, day, pickup, dropoff);
                demands[dem] = prob;
            }
        }

        double query_demand(Demand dem) {
            if (demands.count(dem) > 0) {
                return demands[dem];
            } else {
                return 0;
            }
        }

        double query_demand(int time, int day, int pickup, int dropoff) {
            return query_demand(Demand(time, day, pickup, dropoff));
        }

        double query_demand(int secs, int day, GeoLocation pickup,
                GeoLocation dropoff) {
            return 0;
        }
};

#endif
