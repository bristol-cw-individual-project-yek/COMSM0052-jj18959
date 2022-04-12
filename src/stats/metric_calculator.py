from scipy import stats
import numpy as np

class MetricCalculator:

    def calculate_multiple_runs(all_metrics:list) -> dict:
        total_waiting_times:list = []
        wait_times_per_junction:list = []
        for metrics in all_metrics:
            total_waiting_times.extend(metrics["wait_time_metrics"]["total-wait-time"]["samples"])
            wait_times_per_junction.extend(metrics["wait_time_metrics"]["wait-times-per-junction"]["samples"])
        return MetricCalculator.get_results(total_waiting_times, wait_times_per_junction)


    def calculate(vehicles:dict) -> dict:
        total_waiting_times:list = []
        wait_times_per_junction:list = []
        for vId in vehicles:
            total_waiting_times.append(vehicles[vId].totalTimeSpentWaiting)
            wait_times_per_junction.extend(vehicles[vId].pastWaitTimesAtJunctions)
        return MetricCalculator.get_results(total_waiting_times, wait_times_per_junction)
    
    
    def get_results(total_waiting_times:list, wait_times_per_junction:list):
        results = {
            "total-wait-time"           : {
                "mean"      : np.mean(total_waiting_times),
                "median"    : np.median(total_waiting_times),
                "min"       : int(np.min(total_waiting_times)),
                "max"       : int(np.max(total_waiting_times)),
                "skew"      : stats.skew(total_waiting_times),      # Non-adjusted Fisher-Pearson coefficient of skewness
                "kurtosis"  : stats.kurtosis(total_waiting_times),
                "samples"   : total_waiting_times,
            },
            "wait-times-per-junction"    : {
                "mean"      : np.mean(wait_times_per_junction),
                "median"    : np.median(wait_times_per_junction),
                "min"       : int(np.min(wait_times_per_junction)),
                "max"       : int(np.max(wait_times_per_junction)),
                "skew"      : stats.skew(wait_times_per_junction),      # Non-adjusted Fisher-Pearson coefficient of skewness
                "kurtosis"  : stats.kurtosis(wait_times_per_junction),
                "samples"   : wait_times_per_junction,
            }
        }

        return results