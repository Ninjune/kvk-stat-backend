import json
import msgpack
import time
import tempfile
import os
from typing import Generic, TypeVar, override
import enum
from time import localtime
from datetime import datetime
from constants import IN_DEV, LOG_PATH, META_FILE_PATH
from models.extra_models import JSON, JSONKey

class Status(enum.Enum):
    DEBUG = 0,
    OK = 1,
    WARNING = 2,
    ERROR = 3,

def statusToString(s: Status):
    if(s == Status.DEBUG):
        return "Debug"
    if(s == Status.OK):
        return "OK"
    if(s == Status.WARNING):
        return "Warning"
    if(s == Status.ERROR):
        return "Error"

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

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path: str = LOG_PATH + f"{timestamp}.txt"
log_data = SaveData[str](log_path, "", False)
logging_level = Status.DEBUG if IN_DEV else Status.OK

def log(message: str, status: Status = Status.OK):
    if(int(status.value[0]) < int(logging_level.value[0])):
        return
    t = localtime()
    time = "[" + ("0" if t.tm_hour < 10 else "") + str(t.tm_hour) + ":" \
            + ("0" if t.tm_min < 10 else "") + str(t.tm_min) + ":" \
            + ("0" if t.tm_sec < 10 else "") + str(t.tm_sec) + "] " 


    fullMessage = time + statusToString(status) + ": " + message
    print(fullMessage, flush=True)
    log_data.data += fullMessage + "\n"
    log_data.save()

