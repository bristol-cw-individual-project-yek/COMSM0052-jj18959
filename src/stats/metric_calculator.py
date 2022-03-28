from scipy import stats
import numpy as np

class MetricCalculator:

    def calculate(vehicles:dict) -> dict:
        total_waiting_times:list = []
        wait_times_per_junction:list = []
        for vId in vehicles:
            total_waiting_times.append(vehicles[vId].totalTimeSpentWaiting)
            wait_times_per_junction.extend(vehicles[vId].pastWaitTimesAtJunctions)
        results = {
            "total-wait-time"           : {
                "mean"      : np.mean(total_waiting_times),
                "median"    : np.median(total_waiting_times),
                "min"       : int(np.min(total_waiting_times)),
                "max"       : int(np.max(total_waiting_times)),
                "skew"      : stats.skew(total_waiting_times),      # Non-adjusted Fisher-Pearson coefficient of skewness
                "kurtosis"  : stats.kurtosis(total_waiting_times),
            },
            "wait-times-per-junction"    : {
                "mean"      : np.mean(wait_times_per_junction),
                "median"    : np.median(wait_times_per_junction),
                "min"       : int(np.min(wait_times_per_junction)),
                "max"       : int(np.max(wait_times_per_junction)),
                "skew"      : stats.skew(wait_times_per_junction),      # Non-adjusted Fisher-Pearson coefficient of skewness
                "kurtosis"  : stats.kurtosis(wait_times_per_junction),
            }
        }

        return results