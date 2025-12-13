from api.benchmark_data import PercentileData
from api.models.extra_models import FullBenchmarkData
from rank_percentiles.calculation_methods import calculation_map

def getBenchmarkRank(benchmark: FullBenchmarkData, 
                     percentileData: PercentileData, 
                     steamId: int) -> str:
    """
    gets the overall benchmark rank of 


    Solution: use implemented calculations for types that are implemented, and use benchmark requests for those that aren't impl

    make a map of strings to function pointers with these in them
    """
    rank_calculation = benchmark.evxl_benchmark.rankCalculation
    calc_function = calculation_map.get(rank_calculation)

    if(calc_function is None):
        return ""
    else:
        return calc_function(benchmark, percentileData, steamId)
