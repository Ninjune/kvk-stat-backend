from threading import Thread
from time import sleep
from typing import Any
from flask import Flask, jsonify, request, send_from_directory
from constants import IN_DEV
from graph import gen_graphs
from rank_percentiles.generator import RankCount, RankPercentileGenerator
from util import log

app = Flask(__name__)
app.json.sort_keys = False  # pyright: ignore[reportAttributeAccessIssue]
generator = RankPercentileGenerator()

@app.route("/rank-count")
def rankPercentiles():
    benchmark: str|None = request.args.get("benchmark") 
    difficulty: str|None = request.args.get("difficulty") 

    if(benchmark is None):
        benchmark = ""
    if(difficulty is None):
        difficulty = ""

    res = generator.getRankCounts(True, benchmark, difficulty)

    return jsonify(res)

@app.route("/")
def index():
    return send_from_directory("../data/static", "redoc-static.html")

def size(map: dict[Any, Any]) -> int:
    ret: int = 0
    for map2 in map.values():
        if map2 is float:
            ret += 1
        else:
            ret += size(map2)
    return ret

    
def update_cache():
    while True:
        try:
            log("Updating rank data cache in background...")
            generator.updateCache()
            if(not IN_DEV):
                gen_graphs(RankCount(generator.getRankCounts(False)))
            log("Cached rank data updated!")
            log("Current request count: " + str(generator.percentileData.apiClient.request_count))
        except Exception as e:
            print(f"Background update failed: {e}")
        sleep(24*3600)  # Update every hour
        update_cache()

updater_thread = Thread(target=update_cache, daemon=True)
updater_thread.start()
