#! /bin/bash

set -e

curl http://wallarelvo-tower.csail.mit.edu/essential.zip >> data.zip
unzip data.zip
rm -rf data.zip
