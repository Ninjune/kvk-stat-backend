from dataclasses import dataclass
from models.evxl_models import EvxlBenchmark, EvxlDifficulty
from models.kvk_models import Benchmark

@dataclass
class FullBenchmarkData:
    """aggregates the full available benchmark data for one benchmark"""
    difficulty: EvxlDifficulty
    kvk_benchmark: Benchmark
    evxl_benchmark: EvxlBenchmark
    pass

type JSONKey = str
type JSON = dict[JSONKey, "JSON"] | list["JSON"] | str | int | float | bool | None

