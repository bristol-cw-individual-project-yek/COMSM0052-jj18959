class BoundingBox:

    def __init__(self, lat_min:float, long_min:float, lat_max:float, long_max:float):
        assert(long_max > long_min)
        assert(lat_max > lat_min)
        self.lat_min = lat_min
        self.long_min = long_min
        self.lat_max = lat_max
        self.long_max = long_max
    
    def get_area(self):
        return (self.lat_max - self.lat_min) * (self.long_max - self.long_min)