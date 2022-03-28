from scipy import stats
import numpy as np

class FairnessCalculator:

    def calculate(vehicles:dict) -> dict:
        waiting_times = []
        for vId in vehicles:
            waiting_times.append(vehicles[vId].totalTimeSpentWaiting)
        
        mean = np.mean(waiting_times)
        # Non-adjusted Fisher-Pearson coefficient of skewness
        skew = stats.skew(waiting_times)
        kurtosis = stats.kurtosis(waiting_times)
        
        results = {
            "wait-time-mean"        : mean,
            "wait-time-skew"        : skew,
            "wait-time-kurtosis"    : kurtosis
        }

        return results