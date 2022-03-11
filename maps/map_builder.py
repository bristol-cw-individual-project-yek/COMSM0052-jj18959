import os

def build_map_from_osm(file_path:str, output_path:str = None):
    if not output_path:
        output_path = file_path.replace(".osm", ".net.xml")
    os.system(f"netconvert --osm-files {file_path} -o {output_path}")