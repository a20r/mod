#! /bin/bash

parallel --max-procs=7 --joblog sandbox/log scripts/create_graph_worker.sh ::: sat sun ::: $(seq 0 23)
