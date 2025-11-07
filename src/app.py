import json
from flask import Flask, request
#from rankPercentiles import getRanks
from api.kovaaker import KovaakerClient

app = Flask(__name__)

#@app.route("/rank-percentiles")
#def rankPercentiles():
#    return getRanks(request.args.get("benchmark"))

@app.route("/")
def index():
    client = KovaakerClient()
    res = client.benchmarks(688, 76561198157599986)

    return json.dumps(res.to_json())

if __name__ == '__main__':
    app.run(port=80)
