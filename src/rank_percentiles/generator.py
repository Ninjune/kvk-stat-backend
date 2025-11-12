import json
from api.benchmark_data import PercentileData
from api.models.extra_models import FullBenchmarkData
from api.models.kvk_models import *
from api.models.evxl_models import *
from util import log
from rank_percentiles.calculation import getBenchmarkRank
from constants import *


class RankPercentileGenerator:
    def __init__(self):
        self.percentileData = PercentileData()

    def get_all_rank_percentiles(self) -> dict[str, dict[str, dict[str, int]]]:
        """
        returns the percentiles for ALL benchmarks in the benchmarks.json file
        in the format {name: {difficulty: RankPercentiles}}
        """
        log("Starting to download all rank percentiles!")
        result: dict[str, dict[str, dict[str, int]]] = {}
        with open(EVXL_BENCHMARKS_PATH , "r") as f:
            evxl_benchmark_data = parse_benchmarks_from_json(json.load(f))
        # process evxl data
        for benchmark in evxl_benchmark_data:
            for difficulty in benchmark.difficulties:
                if benchmark.rankCalculation == "vt-energy" and difficulty.difficultyName == "Advanced":
                    (result.setdefault(benchmark.benchmarkName, {})
                    .setdefault(difficulty.difficultyName, self.get_rank_percentiles(difficulty, benchmark))
                    )

        log("")
        for benchmark in result.keys():
            rankedInBenchmark = 0
            log("Benchmark: " + benchmark)
            for difficulty in result[benchmark].keys():
                rankedInDifficulty = 0
                for rank in result[benchmark][difficulty]:
                    log(rank + ": " + str(result[benchmark][difficulty][rank]))
                    rankedInDifficulty += result[benchmark][difficulty][rank]
                log("Total ranked in difficulty " + difficulty + ": " + str(rankedInDifficulty) + "\n")
                rankedInBenchmark += rankedInDifficulty
            log("Total ranked in benchmark (NOTE: overlap expected): " + str(rankedInBenchmark) + "\n")


        return result


    def get_rank_percentiles(self, difficulty: EvxlDifficulty, evxl_data: EvxlBenchmark) -> dict[str, int]:
        """returns the percentiles for one benchmark and it's difficulty"""
        # read from json the map of each scenario name in the benchmarks to the scenario id 
        log("Getting rank percentiles with benchmark=" + evxl_data.benchmarkName 
            + " and difficulty=" + difficulty.difficultyName
            )

        kvk_benchmark_id: int = difficulty.kovaaksBenchmarkId

        log("Requesting Kvk benchmark data with benchmark id=" + str(kvk_benchmark_id) + "...")
        kvk_benchmark_data: Benchmark = self.percentileData.apiClient.benchmarks(kvk_benchmark_id, STEAM_ID)
        log("Successfully requested kvk benchmark data! Updating scenario Id map...")
        for category in kvk_benchmark_data.categories:
            category_data = kvk_benchmark_data.categories[category]
            for scenario in category_data.scenarios:
                scenario_data = category_data.scenarios[scenario]
                scenario_data.rank_maxes
                self.percentileData.scenarioIdMap[scenario] = scenario_data.leaderboard_id

        fullData: FullBenchmarkData = FullBenchmarkData(
                difficulty,
                kvk_benchmark_data, 
                evxl_data, 
                )

        log("Successfully updated scenario id map with size (bytes)=" 
            + str(self.percentileData.scenarioIdMap.__sizeof__())
            + " Appending to benchmark threshold map..."
            )
        # this needs to run for score calculation later
        self.percentileData.append_benchmark_threshold_map(fullData)

        # for all the benchmark scenarios, go through the leaderboard and find
        # the intersection of the sets of steamIds on every scenarios
        # that set is every player that has played every scenario on a benchmark
        id_sets: list[set[int]] = []
        tempSet: set[int] = set()

        # looking for the intersection of the set of the union of all subcategories
        # and set up the scenSteamIdScoreMap
        currentScenInCategory: int = 0
        for category in fullData.difficulty.categories:
            currentScenInCategory = 0
            tempSet = set()
            for subcategory in category.subcategories:
                if("Viscose" in fullData.evxl_benchmark.benchmarkName):
                    currentScenInCategory = 0

                if(evxl_data.benchmarkName == "Voltaic S4" and fullData.difficulty.difficultyName == "Novice"):
                    currentScenInCategory = 0

                for _ in range(subcategory.scenarioCount):
                    categoryName = subcategory.kvkCategoryName
                    scenDict = fullData.kvk_benchmark.categories[categoryName].scenarios
                    scenName: str = list(scenDict.keys())[currentScenInCategory]
                    scenData = scenDict[scenName]
                    self.percentileData.download_leaderboard_scores(fullData, subcategory.subcategoryName, scenName, scenData.leaderboard_id)
                    steamIds = (self.percentileData.scenSteamIdScoreMap.data
                                    [fullData.evxl_benchmark.benchmarkName]
                                    [fullData.difficulty.difficultyName]
                                    [subcategory.subcategoryName]
                                    [scenName].keys()
                                )
                    tempSet = tempSet.union(set(steamIds))
                    currentScenInCategory += 1
                id_sets.append(tempSet)

        log("Created the list of the sets for the benchmark! Len=" + str(len(id_sets)) + " len[0]=" + str(len(id_sets[0])))
        # this set represents all steamIds that have played every scenario
        allIdsInBenchmark: set[int] = id_sets[0]
        for i in range(1, len(id_sets)):
            allIdsInBenchmark = allIdsInBenchmark.intersection(id_sets[i])
        log("Created the set of all ids for the benchmark! Len=" + str(len(allIdsInBenchmark)))

        log("Calculating the rank with rank calculation=" 
            + evxl_data.rankCalculation
        )

        # next, use that set to calculate voltaic rank for every steam id and
        # put that into a map of steamId to rank (for if you want to check rank of 
        # someone later, say for full voltaic ranks)
        rankMap: dict[int, str] = {}
        for steamId in allIdsInBenchmark:
            rankMap[steamId] = getBenchmarkRank(fullData, self.percentileData, steamId)
        log("Created the map of all players to their ranks! Counting up the map...")

        # then count up the numbers of each rank in that map.
        rankCount: dict[str, int] = {}
        rankedInDifficulty: int = 0

        for steamId in rankMap.keys():
            if(rankMap[steamId] == "Celestial"):
                log(str(steamId))
            for rank in fullData.difficulty.rankColors.keys():
                rankCount.setdefault(rank, 0)
                if(rankMap[steamId] == rank):
                    rankCount[rank] += 1
                rankedInDifficulty += 1

        return rankCount
