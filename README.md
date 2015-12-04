# mod
Machine learning for (m)obility (o)n (d)emand

## Extracting Taxi Demand Probabilities
For help on extracting taxi demand probabilities run

    $ python scripts/features.py --help

## Using Demand Predictions in C++
A header file for parsing, querying, and sampling the demand probabilities
is provided in `include/demand.hpp`. A file showing how to determine the
demand probabilities is shown in `include/demand_test.cpp`

## Running Together
To be able to sample from the taxi demand probability distribution, you must
first run the Python script to determine the probabilities from the raw
data. Then you may instantiate a `DemandLookup` object with the files
that were generated from the script.
