from flask import Flask, request
from rankPercentiles import getRanks

app = Flask(__name__)

@app.route("/rank-percentiles")
def rankPercentiles():
    return getRanks(request.args.get("benchmark"))

if __name__ == '__main__':
    app.run(port=80)
