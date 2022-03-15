from scipy import skew
from scipy.stats import kurtosis

class FairnessCalculator:

    def calculate(vehicles:dict) -> dict:
        waiting_times = []
        for vId in vehicles:
            waiting_times.append(vehicles[vId].timeSpentWaiting)
        
        # Non-adjusted Fisher-Pearson coefficient of skewness
        skew = skew(waiting_times)
        kurtosis = kurtosis(waiting_times)
        
        results = {
            "skew"      : skew,
            "kurtosis"  : kurtosis
        }

        return results