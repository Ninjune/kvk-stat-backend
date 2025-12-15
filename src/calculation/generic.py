from dataclasses import dataclass
import json
from types import FunctionType
from models.benchmark_data import PercentileData
from models.evxl_models import EvxlCategory, EvxlSubcategory
from models.extra_models import FullBenchmarkData
from util import log 
logging: bool = False

# variables that are meant to be overriden based on specific rules for subcategories/benchmarks
@dataclass
class SubcategoryOverrideVars:
    current_scen_in_category: int = 0
    avg_count_per_subcategory_override: int = -1
    cap_energy_at_top_rank: bool = False
    skip_subcategory: bool = False

def genericRankCalculate(bm: FullBenchmarkData,
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
            overrideVars = getCategoryExceptions(bm, category, subcategory, currentScenInCategory)
            currentScenInCategory = overrideVars.current_scen_in_category

            avgCount = avgCountPerSubcategory
            if(overrideVars.avg_count_per_subcategory_override != -1):
                avgCount = overrideVars.avg_count_per_subcategory_override

            if(overrideVars.skip_subcategory):
                continue

            for _ in range(subcategory.scenarioCount):
                kvKCategoryName = subcategory.kvkCategoryName
                scenName: str = list(bm.kvk_benchmark.categories[kvKCategoryName].scenarios.keys())[currentScenInCategory]
                currentScenInCategory += 1
                threshold = percentileData.thresholdMap[(bm.evxl_benchmark.benchmarkName, bm.difficulty.difficultyName, scenName)]
                scenScoreData = percentileData.scenSteamIdScoreMap.data[scenName]
                if(scenScoreData.get(steamId) is None): # other scens in the subcategory should have the player
                    continue
                newEnergy = calculateEnergyFunction(threshold, scenScoreData[steamId])

                if(bm.evxl_benchmark.rankCalculation == "vt-energy" and bm.difficulty.difficultyName == "Advanced"):
                    newEnergy = min(newEnergy, (len(threshold)) * 100)

                subcategoryEnergiesForAvg.append(newEnergy)

            subcategoryEnergiesForAvg.sort(reverse=True)
            sum: float = 0

            for i in range(avgCount):
                if(i < len(subcategoryEnergiesForAvg)):
                    sum += subcategoryEnergiesForAvg[i]

            subcategoryEnergy = sum/avgCount

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

def scenRankCalculate(threshold: list[int], score: float) -> float:
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

def _thresholdEnergy(score: float, i: int, currentThreshold: float, previousThreshold: float) -> float:
    """returns energy in the range [0, """
    if(logging):
        log(json.dumps({"score": score, "i": i, "currentThreshold": currentThreshold, "previousThreshold": previousThreshold}))
    return i + (score - previousThreshold)/(currentThreshold - previousThreshold)


def getCategoryExceptions(bm: FullBenchmarkData,
                          category: EvxlCategory,
                          subcategory: EvxlSubcategory, 
                          currentScenInCategory: int
                          ) -> SubcategoryOverrideVars:
    ret: SubcategoryOverrideVars = SubcategoryOverrideVars()
    ret.current_scen_in_category = currentScenInCategory

    if(bm.evxl_benchmark.benchmarkName == "Voltaic S4" and bm.difficulty.difficultyName == "Novice"):
        ret.current_scen_in_category = 0

    if("Viscose" in bm.evxl_benchmark.benchmarkName):
        ret.current_scen_in_category = 0

    if("Jade Palace Ground" in bm.evxl_benchmark.benchmarkName):
        ret.current_scen_in_category = 0

    # Exception for jade palace ground such that the final category only takes the top scenario energy
    if("Jade" in bm.evxl_benchmark.benchmarkName and subcategory.subcategoryName == "Fluidity"):
        ret.avg_count_per_subcategory_override = 1

    # Ignore strafe for VT S4
    if(subcategory.subcategoryName == "Strafe"):
        ret.skip_subcategory = True

    return ret
