from vehicle.policy.policy import Policy

class CustomTestPolicy(Policy):

    def decide_state(self, vehicle, conflicting_vehicles):
        print("This is a custom policy.")
        pass