#! /bin/bash

parallel --jobs 100 \
    --joblog sandbox/log scripts/load_metrics.py ::: \
    $(/bin/ls /home/wallar/nfs/data/data-sim)
