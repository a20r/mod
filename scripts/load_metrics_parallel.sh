#! /bin/bash

parallel --max-procs=24 --joblog sandbox/log scripts/load_metrics.py ::: $(/bin/ls /home/wallar/nfs/data/data-sim)
