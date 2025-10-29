import json
import os
from typing import Final
from api.models import *
from api.kovaaker import KovaakerClient
ID_MAP_PATH = "data/id_map.json"
PERCENTILES_PATH = "data/rank_percentiles.json"


def getRanks(benchmark: str|None) -> RankPercentiles:

    # read from benchmarks and add all scenarios to a list
    usable_scens: list[str] = []


    # read from json the map of each scenario name in the benchmarks to the scenario id 

    id_map: dict[str, int] = {}
    if(os.path.exists(ID_MAP_PATH)):
        with open(ID_MAP_PATH, "r") as f:
            id_map = json.load(f)

    # if the name already maps to an id, skip it
    for scen in benchmark
    id_map[]

    # if not, find the name and add it to the map

    # write to json
    with open(ID_MAP_PATH, "w") as f:
        json.dump(id_map, f)

    # read from json the table of rank percentile data

        # if the last change is more than 24hrs old,

            # recalculate the current percentiles

            # we need a list of scenarios (in a format to be used by the api)
            # that are in each benchmark

            # which endpoints do we need to calculate the percentiles?
            # Scenario details endpoint
            api_client = KovaakerClient()

            api_client.scenario_leaderboard()

            # how do we calculate the percentiles?
            # for each rank, we count the players above the score threshold but below
            # the score threshold of the next rank

        # else 

            # use existing data

        # write to json

    return 
