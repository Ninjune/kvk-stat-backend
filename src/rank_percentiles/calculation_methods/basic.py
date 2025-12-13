from api.benchmark_data import PercentileData
from api.models.extra_models import FullBenchmarkData
from rank_percentiles.calculation_methods.generic import genericRankCalculate, scenRankCalculate

def basic(bm: FullBenchmarkData,
          percentileData: PercentileData,
          steamId: int
          ) -> str:
    """
    Each subcategory is ranked based on its best-performing scenario.

    The final rank is determined by the lowest of these subcategory ranks.
    If any subcategory is unranked, the overall rank will also be unranked.
    """

    return genericRankCalculate(bm, 
                                percentileData, 
                                steamId, 
                                scenRankCalculate, 
                                min,
                                1
                                )

