#! /bin/bash

set -e

wget http://wallarelvo-tower.csail.mit.edu/essential.zip
unzip essential.zip
mv essential data
rm -rf essential.zip

head -n 10000 data/trip_data_5.csv > data/trip_data_short.csv
