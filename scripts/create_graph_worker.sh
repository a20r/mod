#! /bin/bash

ROOTDIR="/media/wallarelvo/JAM-DRL/data-network/manhattan"
DIR=$ROOTDIR/$1-$2

echo $DIR

python scripts/create_nyc_graph.py \
    --fn_edge_times $1.csv \
    --hour $2 \
    --fn_graph $DIR/manhattan_graph.pickle \
    --fn_paths $DIR/paths.csv \
    --fn_times $DIR/times.csv
