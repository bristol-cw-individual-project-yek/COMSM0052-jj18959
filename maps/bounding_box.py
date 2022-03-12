class BoundingBox:

    def __init__(self, lat_min:float, long_min:float, lat_max:float, long_max:float):
        assert(long_max >= long_min)
        assert(lat_max >= lat_min)
        self.lat_min = lat_min
        self.long_min = long_min
        self.lat_max = lat_max
        self.long_max = long_max
    
    def get_area(self):
        return (self.lat_max - self.lat_min) * (self.long_max - self.long_min)
    
    def from_origin(origin_lat:float, origin_long:float, width:float, height:float):
        lat_min = origin_lat - height/2.0
        lat_max = origin_lat + height/2.0
        long_min = origin_long - width/2.0
        long_max = origin_long + width/2.0
        bbox = BoundingBox(lat_min, long_min, lat_max, long_max)
        return bbox