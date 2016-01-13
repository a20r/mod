
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

#define INTERVAL_SIZE (60 * 15);

namespace mod
{

    class GeoLocation
    {
        public:
            double lat, lon;
            GeoLocation() {};
            ~GeoLocation() {};
            GeoLocation(double lat, double lon) : lat(lat), lon(lon)
            {
            };

            double distance(GeoLocation& gl)
            {
                double lat1 = lat;
                double lon1 = lon;
                double lat2 = gl.lat;
                double lon2 = gl.lon;
                lon1 = lon1 * (M_PI / 180.0);
                lat1 = lat1 * (M_PI / 180.0);
                lon2 = lon2 * (M_PI / 180.0);
                lat2 = lat2 * (M_PI / 180.0);
                double dlon = lon2 - lon1;
                double dlat = lat2 - lat1;
                double a = pow(sin(dlat / 2.0), 2) + cos(lat1) * cos(lat2)
                    * pow(sin(dlon / 2.0), 2);
                double c = 2 * asin(sqrt(a));
                double dist_km = 6367 * c;
                return dist_km;
            }
    };

    class Time
    {
        public:
            int day, secs;

            Time() {};
            ~Time() {};
            Time(int day, int secs) : day(day), secs(secs)
            {
            };

            int get_interval() const
            {
                return secs / INTERVAL_SIZE;
            }
    };

    class Demand
    {
        public:
            int tau, day, pickup, dropoff;

            Demand() {};
            Demand(int tau, int day, int pickup, int dropoff) :
                tau(tau), day(day), pickup(pickup), dropoff(dropoff)
            {
            }
    };

    class DemandHash {
        public:
            size_t operator() (const Demand& demand) const
            {
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

    inline bool operator<= (Time const& lhs, Demand const& rhs) {
        return lhs.day <= rhs.day and lhs.get_interval() <= rhs.tau;
    };

    inline bool operator> (Time const& lhs, Demand const& rhs) {
        return lhs.day >= rhs.day and lhs.get_interval() > rhs.tau;
    };

    inline bool operator>= (Time const& lhs, Demand const& rhs) {
        return lhs.day >= rhs.day and lhs.get_interval() >= rhs.tau;
    };

    inline ostream& operator<< (ostream& os, const Demand& demand) {
        os << "Demand(";
        os << demand.tau << ", ";
        os << demand.day << ", ";
        os << demand.pickup << ", ";
        os << demand.dropoff;
        os << ")";
        return os;
    };

    class DemandLookup
    {
        private:
            unordered_map<Demand, double, DemandHash> demands;
            vector<Demand> demand_vec;
            vector<double> cum_sum;
            vector<GeoLocation> stations;
            vector<vector<double>> times;

        public:
            DemandLookup() {};
            ~DemandLookup() {};

            DemandLookup(string fn_stations, string fn_probs, string fn_times)
            {
                init(fn_stations, fn_probs, fn_times);
            }

            void init(string fn_stations, string fn_probs, string fn_times)
            {
                load_probs(fn_probs);
                load_stations(fn_stations);
                load_times(fn_times);
            }

            void load_probs(string fn_probs)
            {
                int tau, day, pickup, dropoff;
                double prob;
                ifstream data(fn_probs);
                string line;
                getline(data, line);

                double lp = 0;
                while(getline(data, line))
                {
                    stringstream lineStream(line);
                    string cell;
                    int counter = 0;
                    while(std::getline(lineStream, cell, ','))
                    {
                        switch (counter++)
                        {
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

            void load_stations(string fn_stations)
            {
                double lat, lon;
                ifstream data(fn_stations);
                string line;
                getline(data, line);

                while(getline(data, line))
                {
                    stringstream lineStream(line);
                    string cell;
                    int counter = 0;
                    while(std::getline(lineStream, cell, ','))
                    {
                        switch (counter++)
                        {
                            case 1: lat = stof(cell);
                            case 2: lon = stof(cell);
                            default: break;
                        }
                    }
                    stations.push_back(GeoLocation(lat, lon));
                }
            }

            void load_times(string fn_times)
            {
                ifstream data(fn_times);
                string line;
                getline(data, line);

                while(getline(data, line))
                {
                    times.push_back(vector<double>());
                    stringstream lineStream(line);
                    string cell;
                    while(std::getline(lineStream, cell, ' '))
                    {
                        times.back().push_back(stof(cell));
                    }
                }
            }

            double get_travel_time_estimate(double lat, double lon, int station)
            {
                GeoLocation gl(lat, lon);
                int closest_station = get_station(gl);
                double dist = get_station(closest_station).distance(gl);
                return dist + times[closest_station][station];
            }

            int get_station(GeoLocation gl)
            {
                double min_dist;
                int min_id;
                for (size_t i = 0; i < stations.size(); i++)
                {
                    double dist = stations[i].distance(gl);
                    if (i == 0)
                    {
                        min_id = 0;
                        min_dist = dist;
                    }
                    else
                    {
                        if (dist < min_dist)
                        {
                            min_id = i;
                            min_dist = dist;
                        }
                    }
                }
                return min_id;
            }

            GeoLocation get_station(int id)
            {
                return stations[id];
            }

            double query_demand(Demand dem)
            {
                if (demands.count(dem) > 0)
                {
                    return demands[dem];
                }
                else
                {
                    return 0;
                }
            }

            double query_demand(int tau, int day, int pickup, int dropoff)
            {
                return query_demand(Demand(tau, day, pickup, dropoff));
            }

            double query_demand(int secs, int day, GeoLocation pickup,
                    GeoLocation dropoff)
            {
                int p_st = get_station(pickup);
                int d_st = get_station(dropoff);
                int tau = secs / (60 * 15);
                return query_demand(tau, day, p_st, d_st);
            }

            void sample(int num, vector<double>& csum, vector<Demand> dems)
            {
                for (int i = 0; i < num; i++)
                {
                    double rnd = (double) rand() / (double) (RAND_MAX);
                    double r = csum[0] + (csum.back() - csum[0]) * rnd;
                    for (size_t j = 0; j < csum.size(); j++)
                    {
                        if (r < csum[j])
                        {
                            dems[i] = demand_vec[j];
                            break;
                        }
                    }
                }
            }

            void sample(int num, Time st, Time end, Demand dems[])
            {
                // This only works if the probability file is sorted by time
                vector<double> csum;
                double lp = 0;
                for (size_t i = 0; i < demand_vec.size(); i++)
                {
                    if (end > demand_vec[i])
                    {
                        break;
                    }
                    else if (st <= demand_vec[i] and end >= demand_vec[i])
                    {
                        csum.push_back(lp + demands[demand_vec[i]]);
                        lp += demands[demand_vec[i]];
                    }
                }
                return sample(num, csum, dems);
            }
    };
};

#endif
