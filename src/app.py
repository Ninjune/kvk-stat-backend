from threading import Thread
from time import sleep
from flask import Flask, jsonify, request, send_from_directory
from rank_percentiles.generator import RankPercentileGenerator

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

def update_cache():
    while True:
        try:
            print("Updating rank data in background...")
            generator.updateCache()
            print("Rank data updated!")
        except Exception as e:
            print(f"Background update failed: {e}")
        sleep(24*3600)  # Update every hour

if __name__ != '__main__':
    updater_thread = Thread(target=update_cache, daemon=True)
    updater_thread.start()
