# mod
Machine learning for *m*obility *o*n *d*emand

# Data Analysis and Feature Extraction
## To Use Open Street Maps
    1. Update the polygonal area in the `nyc_poly` variable in `common.py`
    2. Run `python scripts/create_query.py` to print the query for the OSM
    data
    3. Download the OSM data from `http://overpass-api.de/query_form.html`
    using the query created from the command above
    4. Run `python scripts/create_osm_graph.py` to generate the pickled python
    graph
    5. Filter the data file to only include the appropriate data points using
    `python scripts/filter_data_file.py`
    6. Run `python scripts/create_data_files.py` to create the CSV files used
    for running the mobility on demand algorithms
