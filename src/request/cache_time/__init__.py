import json
from typing import Any
from models.evxl_models import EvxlBenchmark, parse_benchmarks_from_json
from request.rank_percentiles import RankPercentileGenerator
from constants import EVXL_BENCHMARKS_PATH

def get_cache_time(generator: RankPercentileGenerator) -> dict[str, int|dict[Any, Any]]:
    ret: dict[str, int|dict[Any, Any]] = {"intervalS": generator.savedRankCount.cacheInterval, "benchmarks": {}}
    evxl_benchmark_data: list[EvxlBenchmark] = []

    with open(EVXL_BENCHMARKS_PATH , "r") as f:
        evxl_benchmark_data = parse_benchmarks_from_json(json.load(f))

    for benchmark in evxl_benchmark_data:
        for difficulty in benchmark.difficulties:
            last_save_time = generator.savedRankCount.getLastSaveTime([benchmark.benchmarkName, difficulty.difficultyName])
            ret["benchmarks"].setdefault(benchmark.benchmarkName, {})[difficulty.difficultyName] = last_save_time  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

    return ret
