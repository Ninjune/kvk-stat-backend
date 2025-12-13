import statistics
from api.benchmark_data import PercentileData
from api.models.extra_models import FullBenchmarkData
from rank_percentiles.calculation_methods.generic import genericRankCalculate, scenRankCalculate


def jade_palace_ground(bm: FullBenchmarkData,
                       percentileData: PercentileData,
                       steamId: int) -> str:
    return genericRankCalculate(bm, 
                                percentileData, 
                                steamId, 
                                scenRankCalculate, 
                                statistics.harmonic_mean, 
                                3
                                )

