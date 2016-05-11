#! /bin/bash

parallel --max-procs=32 \
    --joblog sandbox/log scripts/load_metrics.py ::: \
    $(/bin/ls /home/wallar/nfs/data/data-sim)
