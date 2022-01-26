class Protocol:
    def __init__(self):
        self.conflicting_vehicleIds = []
    
    
    def resolve_conflicts(self):
        for vId in self.conflicting_vehicleIds:
            self.resolve_conflict(vId)

    
    def resolve_conflict(self, vId):
        print(vId)