
import common
import planar


query_template = """
<?xml version="1.0"?>
<osm-script>
    <query type="node">
        <bbox-query s="{1}" n="{3}" w="{0}" e="{2}"/>
    </query>
    <query type="way">
        <bbox-query s="{1}" n="{3}" w="{0}" e="{2}"/>
    </query>
    <union>
        <item/>
        <recurse type="down"/>
    </union>
    <print/>
</osm-script>
"""


def get_query():
    poly = planar.Polygon.from_points(common.nyc_poly)
    r = poly.bounding_box
    box = (r.min_point.x, r.min_point.y, r.max_point.x, r.max_point.y)
    return query_template.format(*box)


if __name__ == "__main__":
    query = get_query()
    print query
