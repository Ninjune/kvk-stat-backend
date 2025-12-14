from dataclasses import dataclass
from models.evxl_models import EvxlBenchmark
from models.extra_models import JSON

@dataclass
class AddBenchmarkData:
    evxl_data: EvxlBenchmark
    exceptions: str

def addBenchmark(data: JSON):
    pass
