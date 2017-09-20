# mod
Machine learning and data analysis for **m**obility **o**n **d**emand

# Installing dependencies
This assumes you have Python 2.7 and pip

`$ ./install.sh`

# Getting some data

`$ scripts/download_data.sh`

This will create a `data/` directory if one does not already exist. It
downloads essential data for creating the experimental data needed to run the
ridesharing experiments

# To create a small dataset

Running the preprocessing on the entire dataset takes a long time. For
debugging and experimentation, I recommend using only a small portion of the
file. The command below will make a new file in `data/` called
`trip_data_short.csv`. This file contains 10000 lines of `trip_data_5.csv`

`$ head -n 10000 data/trip_data_5.csv > data/trip_data_short.csv`

# Create data for experiments

`$ scripts/create_mod_files.sh [output dir for new files]`
