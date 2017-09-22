#scripts/download_data.sh
set -e
sudo pip install -r requirements.txt
mkdir -p third_party
git clone https://github.com/rogersce/cnpy third_party/cnpy
mkdir -p third_party/cnpy/build
cd third_party/cnpy; git reset --hard b39d58d3640f77c043bfe92591afeafdd82e78db; cd -;
cd third_party/cnpy/build; cmake ..; cd -;
cd third_party/cnpy/build; make && sudo make install; cd -;
