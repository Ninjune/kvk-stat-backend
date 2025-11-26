from dataclasses import dataclass
import json
import msgpack
import time
import tempfile
import os
from typing import Generic, TypeVar, override
from api.models.evxl_models import EvxlBenchmark, EvxlDifficulty
from api.models.kvk_models import Benchmark
from constants import META_FILE_PATH

@dataclass
class FullBenchmarkData:
    """aggregates the full available benchmark data for one benchmark"""
    difficulty: EvxlDifficulty
    kvk_benchmark: Benchmark
    evxl_benchmark: EvxlBenchmark
    pass

type JSONKey = str
type JSON = dict[JSONKey, "JSON"] | list["JSON"] | str | int | float | bool | None

class MetaData(dict[JSONKey, JSON]): pass

T = TypeVar('T')
class SaveData(Generic[T]):
    def __init__(self, path: str, default: T = None, json: bool = True):
        self.path = path
        self.data: T = default
        self.json = json
        self.load()

    def save(self):
        try:
            data: bytes|str|None = None
            mode = 'wb' if self.json else 'w'

            if(self.json):
                data = msgpack.packb(self.data)
            else:
                data = str(self.data)

            dir_name = os.path.dirname(self.path) or '.'
            os.makedirs(dir_name, exist_ok=True)
            
            with tempfile.NamedTemporaryFile(mode=mode, dir=dir_name, delete=False) as tmp_file:
                tmp_path = tmp_file.name
                if self.json:
                    tmp_file.write(data)
                else:
                    tmp_file.write(data)
            
            os.replace(tmp_path, self.path)

            with open(self.path, mode) as f:
                f.write(data)

        except FileNotFoundError:
            print("Unable to save data!")

    def load(self):
        try:
            with open(self.path, "rb") as f:
                data_bytes = f.read()
            self.data = msgpack.unpackb(data_bytes, raw=False)
        except FileNotFoundError:
            pass # use default

class CachedData(SaveData[T]):
    def __init__(self, path: str, cacheInterval: int, default: T = None, json: bool = True):
        super().__init__(path, default, json)
        self.cacheInterval = cacheInterval

    @override
    def save(self, JSONPath: list[JSONKey] = []):
        super().save()
        meta_data: MetaData = MetaData()

        try:
            with open(META_FILE_PATH, "r") as f:
                meta_data = json.load(f)
        except FileNotFoundError:
            pass

        JSONPath.insert(0, self.path)
        self._evalPath(meta_data, JSONPath, int(time.time()))
       
        try:
            with open(META_FILE_PATH, "w") as f:
                f.write(json.dumps(meta_data))
        except:
            print("Unable to save meta data!")

    def shouldUseCache(self, JSONPath: list[JSONKey]) -> bool:
        return time.time() - self.getLastSaveTime(JSONPath) <= self.cacheInterval

    def getLastSaveTime(self, JSONPath: list[JSONKey]) -> int:
        """Returns seconds since epoch (time.time()) of last save"""
        meta_data: MetaData = MetaData()

        try:
            with open(META_FILE_PATH, "r") as f:
                meta_data = json.load(f)
        except FileNotFoundError:
            pass

        JSONPath.insert(0, self.path)
        val: JSON = self._evalPath(meta_data, JSONPath)

        if(val is None): # not found
            return 0
        if(not isinstance(val, int)):
            raise TypeError(f"Expected int, got {type(val)}")
        return val

    def _evalPath(self, start: dict[JSONKey, JSON], JSONPath: list[JSONKey], value: JSON = None) -> JSON | None:
        point = start

        for p in range(len(JSONPath)-1):
            if not isinstance(point, dict):
                raise TypeError(f"Expected dict, got {type(point)}")

            if JSONPath[p] not in point.keys():
                point[JSONPath[p]] = {}

            point = point[JSONPath[p]]

        if(isinstance(point, dict)):
            if(value is not None):
                point.update({JSONPath[len(JSONPath)-1]: value})
            return point.get(JSONPath[len(JSONPath)-1])
        else:
            raise TypeError(f"Expected dict at end of eval, got {type(point)}")
