import statistics
from models.benchmark_data import PercentileData
from models.extra_models import FullBenchmarkData
from calculation.generic import genericRankCalculate, scenRankCalculate

def vt_energy(bm: FullBenchmarkData,
              percentileData: PercentileData,
              steamId: int) -> str:
    return genericRankCalculate(bm, 
                                percentileData, 
                                steamId, 
                                scenRankCalculate, 
                                statistics.harmonic_mean, 
                                1
                                )

