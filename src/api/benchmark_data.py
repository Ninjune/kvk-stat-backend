from api.kovaaker import KovaakerClient
from api.models.extra_models import FullBenchmarkData, SaveData
from api.models.kvk_models import BenchmarkCategory, BenchmarkScenario
from util import log
from constants import *

class PercentileData:
    def __init__(self):
        self.apiClient = KovaakerClient()
        self.scenarioIdMap: dict[str, int] = {}
        """map of each scenario name to kvk id"""
        self.thresholdMap: dict[tuple[str, str, str], list[int]] = {}
        """map of each benchmark name/difficulty name/scenario to the thresholds on that scen"""

        self.scenSteamIdScoreMap = SaveData[dict[str, dict[str, dict[str, dict[str, dict[int, float]]]]]](SCEN_SCORE_MAP_PATH, {})
        """map of each benchmark, difficulty, category, scenario to the steamId: score of that respective scenario"""
        self.scenSteamIdScoreMap.load()
        pass

    def append_benchmark_threshold_map(self, benchmark: FullBenchmarkData) -> None:
        """
        appends to the threshold map a new benchmark, which is a map of tuples of 
        ((evxl) benchmark names, (evxl) benchmark difficulties, scenario name) to score thresholds
        """
        for category in benchmark.kvk_benchmark.categories.keys():
            categoryData: BenchmarkCategory = benchmark.kvk_benchmark.categories[category]
            for scenario in categoryData.scenarios.keys():
                scenarioData: BenchmarkScenario = categoryData.scenarios[scenario]
                key = (benchmark.evxl_benchmark.benchmarkName, benchmark.difficulty.difficultyName, scenario)
                self.thresholdMap[key] = scenarioData.rank_maxes

    def download_leaderboard_scores(self, bmd: FullBenchmarkData, subcategory: str, scen: str, leaderboardId: int) -> None:
                log("Downloading leaderboard for: " + scen)
                scen_found = (self.scenSteamIdScoreMap.data
                    .get(bmd.evxl_benchmark.benchmarkName, {})
                    .get(bmd.difficulty.difficultyName, {})
                    .get(subcategory, {})
                    .get(scen))

                if(scen_found is not None):
                    return

                self.scenSteamIdScoreMap.data \
                    .setdefault(bmd.evxl_benchmark.benchmarkName, {}) \
                    .setdefault(bmd.difficulty.difficultyName, {}) \
                    .setdefault(subcategory, {}) \
                    .setdefault(scen, self.apiClient.scenario_leaderboard(
                        leaderboardId,
                        ["steamId", "score"],
                        True)
                    )
                self.scenSteamIdScoreMap.save()
