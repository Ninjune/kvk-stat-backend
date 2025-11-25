from flask import Flask, jsonify, request
from rank_percentiles.generator import RankPercentileGenerator
#import plotly.express as px

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

    res = generator.getRankCounts(benchmark, difficulty)

    return jsonify(res)

@app.route("/")
def index():
    return "/rank-percentiles -- Returns rank counts"

if __name__ == '__main__':
    app.run(port=443, ssl_context=("/app/certs/fullchain.pem", "/app/certs/privkey.pem"))
    #res = generator.getRankCounts()
