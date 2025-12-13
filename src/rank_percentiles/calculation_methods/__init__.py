
from pathlib import Path
import importlib
from types import FunctionType

calculation_map: dict[str, FunctionType] = {}
for file in Path(__file__).parent.glob("*.py"):
    if file.stem != "__init__":
        mod = importlib.import_module(f".{file.stem}", package=__name__)
        if hasattr(mod, file.stem):
            calculation_map[file.stem.replace("_", "-")] = getattr(mod, file.stem)
