
#ifndef DEMAND_HPP
#define DEMAND_HPP

#include <sstream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <functional>
#include <cmath>
#include <random>

using namespace std;

class GeoLocation {
    public:
        double lat, lon;
        GeoLocation() {};
        ~GeoLocation() {};
        GeoLocation(double lat, double lon) : lat(lat), lon(lon) {};

        double distance(GeoLocation& gl) {
            double dlat2 = pow(gl.lat - lat, 2);
            double dlon2 = pow(gl.lon - lon, 2);
            return sqrt(dlat2 + dlon2);
        }
};

class Demand {
    public:
        int tau, day, pickup, dropoff;

        Demand() {};

        Demand(int tau, int day, int pickup, int dropoff) {
            this->tau = tau;
            this->day = day;
            this->pickup = pickup;
            this->dropoff = dropoff;
        }
};

class DemandHash {
    public:
        size_t operator() (const Demand& demand) const {
            stringstream buffer;
            buffer << demand.tau << " ";
            buffer << demand.day << " ";
            buffer << demand.pickup << " ";
            buffer << demand.dropoff;
            return hash<string>()(buffer.str());
        }
};

inline bool operator== (Demand const& lhs, Demand const& rhs) {
    return lhs.tau == rhs.tau and lhs.day == rhs.day and
        lhs.pickup == rhs.pickup and lhs.dropoff == rhs.dropoff;
};

inline ostream& operator<<(ostream& os, const Demand& demand) {
    os << "Demand(";
    os << demand.tau << ", ";
    os << demand.day << ", ";
    os << demand.pickup << ", ";
    os << demand.dropoff;
    os << ")";
    return os;
};

class DemandLookup {

    private:
        unordered_map<Demand, double, DemandHash> demands;
        vector<Demand> demand_vec;
        vector<double> cum_sum;
        vector<GeoLocation> stations;
        default_random_engine generator;

    public:
        DemandLookup() {};
        ~DemandLookup() {};

        DemandLookup(string fn_stations, string fn_probs) {
            load_probs(fn_probs);
            load_stations(fn_stations);
        }

        void load_probs(string fn_probs) {
            int tau, day, pickup, dropoff;
            double prob;
            ifstream data(fn_probs);
            string line;
            getline(data, line);

            double lp = 0;
            while(getline(data, line)) {
                stringstream lineStream(line);
                string cell;
                int counter = 0;
                while(std::getline(lineStream, cell, ',')) {
                    switch (counter++) {
                        case 0: tau = stoi(cell);
                        case 1: day = stoi(cell);
                        case 2: pickup = stoi(cell);
                        case 3: dropoff = stoi(cell);
                        case 4: prob = stof(cell);
                        default: break;
                    }
                }

                Demand dem(tau, day, pickup, dropoff);
                demands[dem] = prob;
                demand_vec.push_back(dem);
                cum_sum.push_back(lp + prob);
                lp += prob;
            }
        }

        void load_stations(string fn_stations) {
            double lat, lon;
            ifstream data(fn_stations);
            string line;
            getline(data, line);

            while(getline(data, line)) {
                stringstream lineStream(line);
                string cell;
                int counter = 0;
                while(std::getline(lineStream, cell, ',')) {
                    switch (counter++) {
                        case 1: lat = stof(cell);
                        case 2: lon = stof(cell);
                        default: break;
                    }
                }

                stations.push_back(GeoLocation(lat, lon));
            }
        }

        double query_demand(Demand dem) {
            if (demands.count(dem) > 0) {
                return demands[dem];
            } else {
                return 0;
            }
        }

        double query_demand(int tau, int day, int pickup, int dropoff) {
            return query_demand(Demand(tau, day, pickup, dropoff));
        }

        double query_demand(int secs, int day, GeoLocation pickup,
                GeoLocation dropoff) {
            int p_st = get_station(pickup);
            int d_st = get_station(dropoff);
            int tau = secs / (60 * 15);
            return query_demand(tau, day, p_st, d_st);
        }

        int get_station(GeoLocation gl) {
            double min_dist;
            int min_id;
            for (size_t i = 0; i < stations.size(); i++) {
                double dist = stations[i].distance(gl);
                if (i == 0) {
                    min_id = 0;
                    min_dist = dist;
                } else {
                    if (dist < min_dist) {
                        min_id = i;
                        min_dist = dist;
                    }
                }
            }
            return min_id;
        }

        GeoLocation get_station(int id) {
            return stations[id];
        }

        void sample(int num, Demand dem[]) {
            for (int i = 0; i < num; i++) {
                double rnd = (double) rand() / (double) (RAND_MAX);
                double r = cum_sum.back() * rnd;
                for (size_t j = 0; j < cum_sum.size(); j++) {
                    if (r < cum_sum[j]) {
                        dem[i] = demand_vec[j];
                        break;
                    }
                }
            }
        }
};

#endif
