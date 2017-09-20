#! /bin/bash

set -e

wget http://wallarelvo-tower.csail.mit.edu/essential.zip
unzip essential.zip
mv essential data
rm -rf essential.zip
