from dataclasses import dataclass
from typing import Any, Dict, List

# this is AI generated b/c no point to model this data myself
@dataclass
class EvxlSubcategory:
    subcategoryName: str
    scenarioCount: int
    color: str


@dataclass
class EvxlCategory:
    categoryName: str
    color: str
    subcategories: List[EvxlSubcategory]


@dataclass
class EvxlDifficulty:
    difficultyName: str
    kovaaksBenchmarkId: int
    sharecode: str
    rankColors: Dict[str, str]
    categories: List[EvxlCategory]


@dataclass
class EvxlBenchmark:
    benchmarkName: str
    rankCalculation: str
    abbreviation: str
    color: str
    spreadsheetURL: str
    difficulties: List[EvxlDifficulty]

def parseBenchmarkFromDict(data: dict[Any, Any]) -> EvxlBenchmark:
    """Convert a dictionary to a Benchmark dataclass instance."""
    difficulties: list[EvxlDifficulty] = []
    for diff_data in data['difficulties']:
        categories: list[EvxlCategory] = []
        for cat_data in diff_data['categories']:
            subcategories: list[EvxlSubcategory] = [
                EvxlSubcategory(**subcat_data)
                for subcat_data in cat_data['subcategories']
            ]
            categories.append(EvxlCategory(
                cat_data['categoryName'],
                cat_data['color'],
                subcategories
            ))
        
        difficulties.append(EvxlDifficulty(
            diff_data['difficultyName'],
            diff_data['kovaaksBenchmarkId'],
            diff_data['sharecode'],
            diff_data['rankColors'],
            categories
        ))
    
    return EvxlBenchmark(
        data['benchmarkName'],
        data['rankCalculation'],
        data['abbreviation'],
        data['color'],
        data['spreadsheetURL'],
        difficulties
    )


def parse_benchmarks_from_json(json_data: list[dict[Any, Any]]) -> list[EvxlBenchmark]:
    """Convert a list of dictionaries to Benchmark dataclass instances."""
    return [parseBenchmarkFromDict(item) for item in json_data]
