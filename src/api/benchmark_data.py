import json
import os
from types import FunctionType
from api.models.evxl_models import parse_benchmarks_from_json
from api.models.extra_models import BenchmarkDifficulty, FullBenchmarkData
from api.models.kvk_models import BenchmarkCategory, BenchmarkScenario
EVXL_BENCHMARKS_PATH = "data/benchmarks.json"

class BenchmarkData:
    def __init__(self):
        self.benchmark_id_map: dict[BenchmarkDifficulty, int] = BenchmarkData.generate_benchmark_id_map(EVXL_BENCHMARKS_PATH)
        self.scenario_id_map: dict[str, int] = {}
        self.threshold_map: dict[tuple[BenchmarkDifficulty, str], list[int]] = {}
        pass

    def append_benchmark_threshold_map(self, benchmark: FullBenchmarkData):
        """
        appends to the threshold map a new benchmark, which is a map of tuples of 
        ((evxl) benchmark names, (evxl) benchmark difficulties, scenario name) to score thresholds
        """
        for category in benchmark.categories:
            categoryData: BenchmarkCategory = benchmark.categories[category]
            for scenario in categoryData.scenarios:
                scenarioData: BenchmarkScenario = categoryData.scenarios[scenario]
                key = (BenchmarkDifficulty(benchmark.benchmarkName, benchmark.difficulty.difficultyName), scenario)
                self.threshold_map[key] = scenarioData.rank_maxes

    @staticmethod
    def generate_benchmark_id_map(evxl_path: str) -> dict[BenchmarkDifficulty, int]:
        """returns a map of tuples of ((evxl) benchmark names, (evxl) benchmark difficulties) to kvk benchmark ids"""
        map: dict[BenchmarkDifficulty, int] = {}
        evxl_benchmark_data = {}

        if(not os.path.exists(evxl_path)):
            raise ValueError("Evxl path does not exist! The benchmark id map would be empty.")

        with open(evxl_path, "r") as f:
            evxl_benchmark_data = parse_benchmarks_from_json(json.load(f))
        # process evxl data
        for benchmark in evxl_benchmark_data:
            for difficulty in benchmark.difficulties:
                map[BenchmarkDifficulty(benchmark.benchmarkName, difficulty.difficultyName)] = difficulty.kovaaksBenchmarkId

        return map


