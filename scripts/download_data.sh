#! /bin/bash

set -e

wget http://wallarelvo-tower.csail.mit.edu/essential.zip
mkdir -p data
unzip essential.zip -d data
rm -rf essential.zip
