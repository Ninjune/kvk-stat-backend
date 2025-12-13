import json
from time import sleep
from api.benchmark_data import PercentileData
from api.models.extra_models import CachedData, FullBenchmarkData
from api.models.kvk_models import *
from api.models.evxl_models import *
from rank_percentiles.calculation_methods.generic import getCategoryExceptions
from util import Status, log
from rank_percentiles.calculation import getBenchmarkRank
from constants import *

class RankCount(dict[str, dict[str, dict[str, float]]]): pass

class RankPercentileGenerator:
    """Very resource heavy, should only be created once"""
    def __init__(self):
        self.savedRankCount = CachedData[RankCount](RANK_COUNT_MAP_PATH, RANK_COUNT_CACHE_INTERVAL_SECONDS, RankCount())
        # kvk benchmark id to Benchmark
        self.savedBenchmarkMap = CachedData[dict[str, dict[Any, Any]]](KVK_BENCHMARK_MAP_PATH, KVK_BENCHMARK_MAP_INTERVAL_SECONDS, {})
        self.percentileData = PercentileData()

    def updateCache(self):
        log("Updating cache!")
        with open(EVXL_BENCHMARKS_PATH , "r") as f:
            evxl_benchmark_data = parse_benchmarks_from_json(json.load(f))

        for benchmark in evxl_benchmark_data:
            for difficulty in benchmark.difficulties:
                self.getRankCounts(False, benchmark.benchmarkName, difficulty.difficultyName)

    def getRankCounts(self, forceCache: bool = False, filterBenchmark: str = "", filterDifficulty: str = "") -> RankCount:
        """
        returns the percentiles for ALL benchmarks in the benchmarks.json file
        in the format {name: {difficulty: RankPercentiles}}
        """
        log("Starting to download all rank percentiles!", Status.DEBUG)
        result: RankCount = RankCount()

        with open(EVXL_BENCHMARKS_PATH , "r") as f:
            evxl_benchmark_data = parse_benchmarks_from_json(json.load(f))

        for benchmark in evxl_benchmark_data:
            for difficulty in benchmark.difficulties:
                if filterBenchmark in benchmark.benchmarkName and filterDifficulty in difficulty.difficultyName:
                    result.setdefault(benchmark.benchmarkName, {})[difficulty.difficultyName] = self._getRankCount(difficulty, benchmark, forceCache)

        return result

    def _getRankCount(self, difficulty: EvxlDifficulty, evxl_data: EvxlBenchmark, forceCache: bool = False) -> dict[str, float]:
        """returns the percentiles for one benchmark and it's difficulty"""
        # read from json the map of each scenario name in the benchmarks to the scenario id 
        if(forceCache or self.savedRankCount.shouldUseCache([evxl_data.benchmarkName, difficulty.difficultyName])):
            if(forceCache and self.savedRankCount.data.get(evxl_data.benchmarkName, {}).get(difficulty.difficultyName) is None):
                log("Cache is not loaded but we're forcing cache. Returning {}!", Status.DEBUG)
                return {}
            log("Detected valid cache for benchmark! Returning.", Status.DEBUG)
            return self.savedRankCount.data[evxl_data.benchmarkName][difficulty.difficultyName]

        log("Getting rank percentiles with benchmark=" + evxl_data.benchmarkName 
            + " and difficulty=" + difficulty.difficultyName
            )
        kvk_benchmark_id: int = difficulty.kovaaksBenchmarkId
        kvk_benchmark_data: Benchmark|None = None

        log("Requesting Kvk benchmark data with benchmark id=" + str(kvk_benchmark_id) + "...")

        if(self.savedBenchmarkMap.shouldUseCache([str(kvk_benchmark_id)])):
            log("Detected valid cache for kvk benchmark! Skipping download...")
            kvk_benchmark_data = self.percentileData.apiClient.parse_kvk_benchmarks_from_json(self.savedBenchmarkMap.data[str(kvk_benchmark_id)])
        else:
            log("Downloading kvk benchmark!")
            try:
                kvk_benchmark_data = self.percentileData.apiClient.benchmarks(kvk_benchmark_id, STEAM_ID)
            except Exception as e:
                log(f"Sleeping for 60s! Got exception from downloading benchmark: {e}", Status.WARNING)
                sleep(60)
                self._getRankCount(difficulty, evxl_data)
                return {}

            self.savedBenchmarkMap.data[str(kvk_benchmark_id)] = asdict(kvk_benchmark_data)
            self.savedBenchmarkMap.save([str(kvk_benchmark_id)])

        log("Successfully requested kvk benchmark data! Updating scenario Id map...")
        for category in kvk_benchmark_data.categories:
            category_data = kvk_benchmark_data.categories[category]
            for scenario in category_data.scenarios:
                scenario_data = category_data.scenarios[scenario]
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
        # note this loop can be seen twice, once here and once in calculation
        currentScenInCategory: int = 0
        for category in fullData.difficulty.categories:
            currentScenInCategory = 0
            tempSet = set()
            for subcategory in category.subcategories:
                currentScenInCategory = getCategoryExceptions(currentScenInCategory, fullData)

                for _ in range(subcategory.scenarioCount):
                    categoryName = subcategory.kvkCategoryName
                    scenDict = fullData.kvk_benchmark.categories[categoryName].scenarios
                    if(currentScenInCategory > len(scenDict.keys())):
                        raise Exception("currentScenInCategory is invalid! Check benchmark for category exceptions and add to function.")
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
        rankCount: dict[str, float] = {}

        for steamId in rankMap.keys():
            for rank in fullData.difficulty.rankColors.keys():
                rankCount.setdefault(rank, 0)
                if(rankMap[steamId] == rank):
                    rankCount[rank] += 1

        log("Caching rank count!")
        self.savedRankCount.data.setdefault(evxl_data.benchmarkName, {})[difficulty.difficultyName] = rankCount
        self.savedRankCount.save([evxl_data.benchmarkName, difficulty.difficultyName])
        log("Current request count: " + str(self.percentileData.apiClient.request_count))

        return rankCount

    def _logRankCounts(self, result: RankCount):
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

