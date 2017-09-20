#! /bin/bash

set -e
OUT_DIR=$1
mkdir -p $OUT_DIR

NYC_DIR=data/nyc-graph/
EDGE_TIMES_FILE=data/nyc-graph/week.csv
HOUR=avg
GRAPH_FILE=$OUT_DIR/manhattan_graph.pickle
PATHS_FILE=$OUT_DIR/paths.csv
TIMES_FILE=$OUT_DIR/times.csv
RAW_DATA_FILE=data/trip_data_short.csv
CLEANED_DATA_FILE=$OUT_DIR/trip_data_short_cleaned.csv
STATIONS_FILE=$OUT_DIR/stations-mod.csv
JAVIER_STATIONS_FILE=$OUT_DIR/stations_LUT.csv
FREQS_FILE=$OUT_DIR/freqs.npy

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
    --fn_nodes=$NYC_DIR/points.csv \
    --fn_cleaned=$CLEANED_DATA_FILE \
    --fn_javier_stations=$JAVIER_STATIONS_FILE

echo Running find_stations.py
python scripts/find_stations.py \
    --fn_nodes=$NYC_DIR/points.csv \
    --dist=0.45 \
    --fn_stations=$STATIONS_FILE

echo Running compute_probs.py
python scripts/compute_probs.py \
    --fn_cleaned=$CLEANED_DATA_FILE \
    --fn_stations=$STATIONS_FILE \
    --fn_freqs=$FREQS_FILE

echo id,lat,lng > $OUT_DIR/stations.csv
cat $NYC_DIR/points.csv >> $OUT_DIR/stations.csv
