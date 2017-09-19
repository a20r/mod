#! /bin/bash

set -e
NYC_DIR=data/nyc-graph/
EDGE_TIMES_FILE=data/nyc-graph/week.csv
HOUR=0
GRAPH_FILE=data/manhattan_graph.pickle
PATHS_FILE=data/paths.csv
TIMES_FILE=data/times.csv
RAW_DATA_FILE=data/trip_data_short.csv
STATIONS_FILE=data/stations.csv
PROBS_FILE=data/probs.csv
FREQS_FILE=data/freqs.csv

echo Running create_nyc_graph.py
python scripts/create_nyc_graph.py \
    --nyc_dir=$NYC_DIR \
    --fn_edge_times=$EDGE_TIMES_FILE \
    --hour=$HOUR \
    --fn_graph=$GRAPH_FILE \
    --fn_paths=$PATHS_FILE \
    --fn_times=$TIMES_FILE

echo Running create_data_files.py
python scripts/create_data_files.py \
    --fn_raw=$RAW_DATA_FILE \
    --fn_graph=$GRAPH_FILE \
    --fn_stations=$STATIONS_FILE \
    --fn_probs=$PROBS_FILE \
    --fn_freqs=$FREQS_FILE
