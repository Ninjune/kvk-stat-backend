from dataclasses import dataclass
import json
from typing import Any, Generic, TypeVar
from api.models.evxl_models import EvxlBenchmark, EvxlDifficulty
from api.models.kvk_models import Benchmark

@dataclass
class FullBenchmarkData:
    """aggregates the full available benchmark data for one benchmark"""
    difficulty: EvxlDifficulty
    kvk_benchmark: Benchmark
    evxl_benchmark: EvxlBenchmark
    pass

T = TypeVar('T')
class SaveData(Generic[T]):
    def __init__(self, path: str, default: T = None, json: bool = True):
        self.path = path
        self.data: T = default
        self.json = json
        self.load()

    def save(self):
        try:
            stra: str = ""
            if(self.json):
                stra = json.dumps(self.data)
            else:
                stra = str(self.data)
            with open(self.path, "w") as f:
                f.write(stra)
        except FileNotFoundError:
            print("Unable to save data!")

    def load(self):
        try:
            with open(self.path, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            pass # use default
