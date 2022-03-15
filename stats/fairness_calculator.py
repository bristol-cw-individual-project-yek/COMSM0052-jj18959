from scipy import stats

class FairnessCalculator:

    def calculate(vehicles:dict) -> dict:
        waiting_times = []
        for vId in vehicles:
            waiting_times.append(vehicles[vId].timeSpentWaiting)
        
        # Non-adjusted Fisher-Pearson coefficient of skewness
        skew = stats.skew(waiting_times)
        kurtosis = stats.kurtosis(waiting_times)
        
        results = {
            "skew"      : skew,
            "kurtosis"  : kurtosis
        }

        return results