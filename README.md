# TaxiSharing
Predicting taxi demand using taxi location history

# Extracting Taxi Demand Probabilities
For help on extracting taxi demand probabilities run

    $ python scripts/features.py --help

# Using Demand Predictions in C++
A header file for parsing, querying, and sampling the demand probabilities
is provided in `include/demand.hpp`. A file showing how to determine the
demand probabilities is shown in `include/demand_test.cpp`
