from enum import Enum
import json
import statistics
from types import FunctionType
from api.benchmark_data import PercentileData
from api.models.extra_models import FullBenchmarkData
from util import log
logging: bool = False

class SubcategoryCalculationType(Enum):
    MAX = 0,
    AVERAGE = 1,

def getBenchmarkRank(benchmark: FullBenchmarkData, 
                     percentileData: PercentileData, 
                     steamId: int) -> str:
    """
    gets the overall benchmark rank of 


    Solution: use implemented calculations for types that are implemented, and use benchmark requests for those that aren't impl

    make a map of strings to function pointers with these in them
    """
    rank_calculation = benchmark.evxl_benchmark.rankCalculation
    calc_function = getCalculationMap().get(rank_calculation)
    if(calc_function is None):
        return ""
    else:
        return calc_function(benchmark, percentileData, steamId)

def _jadePalaceRankCalculate(bm: FullBenchmarkData,
                                          percentileData: PercentileData,
                                          steamId: int) -> str:
    return _genericRankCalculate(bm, 
                                 percentileData, 
                                 steamId, 
                                 _scenRankCalculate, 
                                 statistics.harmonic_mean, 
                                 3
                                 )

def _voltaicBenchmarkOverallRankCalculate(bm: FullBenchmarkData,
                                          percentileData: PercentileData,
                                          steamId: int) -> str:
    return _genericRankCalculate(bm, 
                                 percentileData, 
                                 steamId, 
                                 _scenRankCalculate, 
                                 statistics.harmonic_mean, 
                                 1
                                 )


def _basicRankCalculate(bm: FullBenchmarkData,
                        percentileData: PercentileData,
                        steamId: int
                        ) -> str:
    """
    Each subcategory is ranked based on its best-performing scenario.

    The final rank is determined by the lowest of these subcategory ranks.
    If any subcategory is unranked, the overall rank will also be unranked.
    """
   
    return _genericRankCalculate(bm, 
                                 percentileData, 
                                 steamId, 
                                 _scenRankCalculate, 
                                 min,
                                 1
                                 )

def _thresholdEnergy(score: float, i: int, currentThreshold: float, previousThreshold: float) -> float:
    """returns energy in the range [0, """
    if(logging):
        log(json.dumps({"score": score, "i": i, "currentThreshold": currentThreshold, "previousThreshold": previousThreshold}))
    return i + (score - previousThreshold)/(currentThreshold - previousThreshold)

def _scenRankCalculate(threshold: list[int], score: float) -> float:
    energy: float = 0;

    # assuming the length of threshold > 2
    if len(threshold) <= 2:
        raise ValueError("The length of the thresholds for a viscose rank must be greater than 2!")

    if(logging):
        log("")
        log("Score: " + str(score) + " Threshold: " + json.dumps(threshold))

    if(score >= threshold[len(threshold)-1]):
        # uses the previous diff b/c there is no other diff to check
        i = len(threshold)-1
        energy = i + (score - threshold[len(threshold)-1])/(threshold[len(threshold)-1] - threshold[len(threshold)-2])
        energy = min(energy, len(threshold))
    else:
        for i in range(len(threshold)):
            if(score < threshold[i]):
                prev_thresh = (threshold[i-1] if i-1 >= 0 else 0);
                energy = _thresholdEnergy(score, i-1, threshold[i], prev_thresh)
                break

    energy = (energy + 1) * 100;
    if(logging):
        log("Energy: " + str(energy))
    assert energy >= 0 # harmonic mean

    if(logging):
        log("")
    return energy

def _genericRankCalculate(bm: FullBenchmarkData,
                          percentileData: PercentileData,
                          steamId: int, 
                          calculateEnergyFunction: FunctionType,
                          calculateAllEnergiesFunction: FunctionType,
                          avgCountPerSubcategory: int = 1
                          ):
    rank = ""
    subcategoryEnergies: list[float] = []

    currentScenInCategory: int = 0
    for category in bm.difficulty.categories:
        currentScenInCategory = 0
        for subcategory in category.subcategories:
            subcategoryEnergiesForAvg: list[float] = []

            # For some reason, this one tracks differently
            if(bm.evxl_benchmark.benchmarkName == "Voltaic S4" and bm.difficulty.difficultyName == "Novice"):
                currentScenInCategory = 0

            # Viscose kvk benchmark tracks differently than voltaic
            if("Viscose" in bm.evxl_benchmark.benchmarkName):
                currentScenInCategory = 0

            # Exception for jade palace ground such that the final category only takes the top scenario energy
            if("Jade" in bm.evxl_benchmark.benchmarkName and subcategory.subcategoryName == "Fluidity"):
                avgCountPerSubcategory = 1
            # note if jade palace ground adds a section below fluidity, it avgCountPerSubcategory will be wrong

            # Ignore strafe for VT S4
            if(subcategory.subcategoryName == "Strafe"):
                continue

            for _ in range(subcategory.scenarioCount):
                categoryName = subcategory.kvkCategoryName
                scenName: str = list(bm.kvk_benchmark.categories[categoryName].scenarios.keys())[currentScenInCategory]
                currentScenInCategory += 1
                threshold = percentileData.thresholdMap[(bm.evxl_benchmark.benchmarkName, bm.difficulty.difficultyName, scenName)]
                #log(scenName + " " + subcategory.subcategoryName)
                scenScoreData = (percentileData.scenSteamIdScoreMap.data[bm.evxl_benchmark.benchmarkName]
                            [bm.difficulty.difficultyName]
                            [subcategory.subcategoryName]
                            [scenName])
                if(scenScoreData.get(steamId) is None): # other scens in the subcategory should have the player
                    continue
                newEnergy = calculateEnergyFunction(threshold, scenScoreData[steamId])

                if(bm.evxl_benchmark.rankCalculation == "vt-energy" and bm.difficulty.difficultyName == "Advanced"):
                    newEnergy = min(newEnergy, (len(threshold)) * 100)

                subcategoryEnergiesForAvg.append(newEnergy)

            subcategoryEnergiesForAvg.sort(reverse=True)
            sum: float = 0

            assert(len(subcategoryEnergiesForAvg) >= avgCountPerSubcategory)

            for i in range(avgCountPerSubcategory):
                sum += subcategoryEnergiesForAvg[i]
            subcategoryEnergy = sum/avgCountPerSubcategory

            subcategoryEnergies.append(subcategoryEnergy)


    energy = calculateAllEnergiesFunction(subcategoryEnergies)
    ranks: list[str] = [rank.name for rank in bm.kvk_benchmark.ranks]

    if(energy < 100):
        rank = ""
    elif(energy >= len(ranks)*100):
        rank = ranks[len(ranks) - 1]
    else:
        rank = ranks[int(energy/100)]

    return rank

def getCalculationMap() -> dict[str, FunctionType]:
    return {"vt-energy": _voltaicBenchmarkOverallRankCalculate, "basic": _basicRankCalculate, "jade-palace-ground": _jadePalaceRankCalculate}

