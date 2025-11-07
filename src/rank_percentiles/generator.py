from api.benchmark_data import BenchmarkData
from api.models.extra_models import BenchmarkDifficulty, FullBenchmarkData
from api.models.kvk_models import *
from api.models.evxl_models import *
from api.kovaaker import KovaakerClient
PERCENTILES_PATH = "data/rank_percentiles.json"


class RankPercentileGenerator:
    def __init__(self):
        self.api_client = KovaakerClient()
        self.benchmarkData = BenchmarkData()

    def get_all_rank_percentiles(self) -> dict[str, dict[str, RankPercentiles]]:
        """
        returns the percentiles for ALL benchmarks in the benchmarks.json file
        in the format {name: {difficulty: RankPercentiles}}
        """

    def get_rank_percentiles(self, bmd: BenchmarkDifficulty, evxl_data: EvxlBenchmark) -> RankPercentiles:
        """returns the percentiles for one benchmark and it's difficulty"""
        # read from json the map of each scenario name in the benchmarks to the scenario id 
        kvk_benchmark_id: int|None = self.benchmarkData.benchmark_id_map.get(bmd) 
        if(kvk_benchmark_id is None):
            raise ValueError("Benchmark or difficulty not found in benchmark id map!")

        kvk_benchmark_data: Benchmark = self.api_client.benchmarks(kvk_benchmark_id, 76561198157599986)
        for category in kvk_benchmark_data.categories:
            category_data = kvk_benchmark_data.categories[category]
            for scenario in category_data.scenarios:
                scenario_data = category_data.scenarios[scenario]
                scenario_data.rank_maxes
                self.benchmarkData.scenario_id_map[scenario] = scenario_data.leaderboard_id

        difficulty: EvxlDifficulty = next((x for x in evxl_data.difficulties if x > 3), None),
        fullData: FullBenchmarkData = FullBenchmarkData.from_parts(
                kvk_benchmark_data, 
                evxl_data, 
                )

        # HERE need a map of {scenarioName: {steamId: score}}

        # read from json the table of rank percentile data

            # if the last change is more than 24hrs old,

                # recalculate the current percentiles
                # this means creating a list of players

                api_client.scenario_leaderboard()


            # else 

                # use existing data

            # write to json

        return 


