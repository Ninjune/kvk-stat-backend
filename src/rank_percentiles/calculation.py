import statistics
from types import FunctionType
from api.models.extra_models import BenchmarkDifficulty, FullBenchmarkData


def getBenchmarkRank(benchmark: FullBenchmarkData, 
                     thresholdMap: dict[tuple[BenchmarkDifficulty, str], list[int]], 
                     score: float) -> str:
    """
    two options: use benchmark request on every single steam id (obtained from each player on all benchmark scen maps) 
    (more api requests, but more general for any benchmark calculation)
    OR calculate the score based on the scoring method of the benchmark using the score from the leaderboard 
    (restricted to only benchmark calculations that have been implemented, but less api requests)

    Solution: use implemented calculations for types that are implemented, and use benchmark requests for those that aren't impl

    make a map of strings to function pointers with these in them
    """
    rank_calculation = benchmark.rankCalculation
    calc_function = getCalculationMap().get(rank_calculation)
    if(calc_function is None):
        return unknownRankCalculate(benchmark, thresholdMap, score)
    else:
        return calc_function(benchmark, thresholdMap, score)

def voltaicBenchmarkOverallRankCalculate(bm: FullBenchmarkData,
                                         thresholdMap: dict[tuple[BenchmarkDifficulty, str],
                                                            list[int]],
                                         score: float
                                         ) -> str:
    currentScenInCategory: int = 0
    rank = ""
    energies: list[float] = []

    for category in bm.difficulty.categories:
        currentScenInCategory = 0
        for subcategory in category.subcategories:
            subcategoryEnergy = -1
            for _ in range(subcategory.scenarioCount):
                scenName: str = list(bm.categories[category.categoryName].scenarios.keys())[currentScenInCategory]
                threshold = thresholdMap[(BenchmarkDifficulty(bm.benchmarkName, bm.difficulty.difficultyName), scenName)]
                newEnergy: float = voltaicScenRankCalculate(
                        threshold,
                        1,
                        scenName
                        )
                if(newEnergy > subcategoryEnergy):
                    subcategoryEnergy = newEnergy
                currentScenInCategory += 1
            energies.append(subcategoryEnergy)

    energy = statistics.harmonic_mean(energies)

    ranks: list[str] = [rank.name for rank in bm.ranks]

    if(energy < 0):
        rank = ""
    elif(energy > len(ranks)):
        rank = ranks[len(ranks) - 1]
    else:
        rank = ranks[int(energy)]

    return rank


def voltaicScenRankCalculate(threshold: list[int], score: float, scenName: str) -> float:
    # offset energy to 0, if it's negative, they're not this rank so it doesn't matter
    energy: float = 0;

    # assuming the length of threshold > 2
    if len(threshold) <= 2:
        raise ValueError("The length of the thresholds for a voltaic rank must be greater than 2!")

    if(score > threshold[len(threshold)-1]):
        prev_thresh = threshold[len(threshold)-1]
        # uses the previous diff b/c there is no other diff to check
        energy = voltaicEnergy(score, len(threshold), prev_thresh, threshold[len(threshold)-2])
    else:
        for i in range(len(threshold)):
            if(score < threshold[i]):
                prev_thresh = (threshold[i-1] if i-1 >= 0 else 0);
                energy = voltaicEnergy(score, i, threshold[i], prev_thresh)

    return energy

@staticmethod
def voltaicEnergy(score: float, i: int, currentThreshold: float, previousThreshold: float) -> float:
    return (i-1) + (score - previousThreshold)/(currentThreshold - previousThreshold)

def basicRankCalculate(benchmark: FullBenchmarkData,
                       thresholdMap: dict[tuple[BenchmarkDifficulty, str],
                                          list[int]],
                       score: float
                       ) -> str:
    """
    Each subcategory is ranked based on its best-performing scenario.

    The final rank is determined by the lowest of these subcategory ranks.
    If any subcategory is unranked, the overall rank will also be unranked.
    """
    return ""

def unknownRankCalculate(benchmark: FullBenchmarkData, 
                         thresholdMap: dict[tuple[BenchmarkDifficulty, str],
                                            list[int]],
                         score: float) -> str:
    """
    Uses benchmark request to get the ranks.

    Don't include this in the calculation map.
    """
    return ""

def getCalculationMap() -> dict[str, FunctionType]:
    return {"vt-energy": voltaicBenchmarkOverallRankCalculate, "basic": basicRankCalculate}

