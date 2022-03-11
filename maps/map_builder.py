import os
from urllib.error import HTTPError
import wget
from maps.bounding_box import BoundingBox
import ssl

def build_map_from_osm(file_path:str, output_path:str = None):
    if not output_path:
        output_path = file_path.replace(".osm", ".net.xml")
    os.system(f"netconvert --osm-files {file_path} -o {output_path}")


def get_osm_area(bbox:BoundingBox, output_file:str):
    ssl._create_default_https_context = ssl._create_unverified_context
    if not output_file.endswith(".osm"):
        output_file += ".osm"
    try:
        wget.download(f"http://api.openstreetmap.org/api/0.6/map?bbox={bbox.lat_min},{bbox.long_min},{bbox.lat_max},{bbox.long_max}", output_file)
    except HTTPError as e:
        print(str(e))
        if bbox.get_area > 0.25:
            print("The area of your bounding box is too big (max is 0.25).")
        else:
            print("You may have requested a map with too many nodes (limit is 50000).")
        quit()