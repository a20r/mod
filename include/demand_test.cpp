
#include <iostream>
#include "demand.hpp"

using namespace std;

int main() {
    DemandLookup dl("../models/probs.txt", "");
    cout << dl.query_demand(0, 2, 11, 2) << endl;
}
