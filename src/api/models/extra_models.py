from dataclasses import asdict, dataclass
from api.models.evxl_models import EvxlBenchmark, EvxlDifficulty
from api.models.kvk_models import Benchmark

@dataclass
class BenchmarkDifficulty:
    name: str
    difficulty: str

@dataclass
class FullBenchmarkData(Benchmark, EvxlBenchmark):
    """aggregates the full available benchmark data for one benchmark"""
    @classmethod
    def from_parts(cls, benchmark: Benchmark, evxl: EvxlBenchmark, bmd: EvxlDifficulty):
        return cls(
            difficulty = bmd,
            **asdict(benchmark),
            **asdict(evxl),
        )

    difficulty: EvxlDifficulty

    pass
