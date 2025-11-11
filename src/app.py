import json
from flask import Flask, request
from api.kovaaker import KovaakerClient
from rank_percentiles.generator import RankPercentileGenerator

app = Flask(__name__)

#@app.route("/rank-percentiles")
#def rankPercentiles():
#    return getRanks(request.args.get("benchmark"))

@app.route("/")
def index():
    generator = RankPercentileGenerator()
    res = generator.get_all_rank_percentiles()

    return res

if __name__ == '__main__':
    app.run(port=80)
