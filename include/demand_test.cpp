
#include <iostream>
#include <random>
#include "demand.hpp"

using namespace std;

void test_query(mod::DemandLookup& dl)
{
    mod::GeoLocation p_st(-73.991788392187516, -73.991788392187516);
    mod::GeoLocation d_st(-73.78195999999997,-73.78195999999997);
    double prob = dl.query_demand(0, 2, p_st, d_st);

    cout << "==================== Query Test ====================" << endl;
    cout << "Probability -> " << prob << endl << endl;
}

void test_sample(mod::DemandLookup& dl)
{
    const int num = 400;
    vector<mod::Demand> dems;
    mod::Time st(4, 810), end(4, 1710);
    bool could_sample = dl.sample(num, st, end, dems);

    cout << "==================== Sample Test ====================" << endl;
    if (could_sample)
    {
        cout << "Sampling " << num << " Demands" << endl;
        for (int i = 0; i < num; i++) {
            cout << "\t" << dems[i] << endl;
        }
        cout << endl;
    }
    else
    {
        cout << "Unable to sample due to lack of data" << endl;
    }
}

void test_path_lookup(mod::DemandLookup& dl)
{
    cout << "==================== Path Lookup Test ====================";
    cout << endl;
    vector<int> path;
    vector<double> times;
    bool got_path = dl.get_path(0, 10, path, times);

    if (got_path)
    {
        cout << "Path: " << endl;
        for (size_t i = 0; i < path.size(); i++)
        {
            cout << "\t" << path[i] << endl;;
        }
        cout << endl;
    }
    else
    {
        cout << "No Path Found!!!" << endl;
    }
}

void test_request_freqs(mod::DemandLookup& dl)
{
    cout << "==================== Request Frequency Test ====================";
    cout << endl;
    mod::Time st(4, 810), end(4, 1710);
    int num = dl.compute_number_of_samples(st, end);
    cout << "\tExpeced number of samples: " << num << endl;
}


int main() {
    srand(time(NULL));
    mod::DemandLookup dl("../data/stationsLUT.csv",
            "../data/probs.csv",
            "../data/distances.csv",
            "../data/paths.csv",
            "../data/freqs.csv");
    test_query(dl);
    test_sample(dl);
    test_path_lookup(dl);
    test_request_freqs(dl);
}
