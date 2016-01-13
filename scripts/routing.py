
import osm
import osm2nx


def init_graph(left, bottom, right, top):
    osm_data = osm.download_osm(left, bottom, right, top)
    G = osm.read_osm(osm_data)
    G, max_distance = osm2nx.make_weighted(G)
    return osm2nx.simplify_by_degree(G, max_distance)

# data = nx.all_pairs_shortest_path(G)
