from flask import Flask, make_response, jsonify, send_from_directory
import pymongo
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
client = pymongo.MongoClient("mongodb://localhost:27017/")

database = client["dictmerge"]
collection = database["wordnet"]
collectionPolnet = database["polnet"]


# @app.route('/static/js/<path:path>')
# def send_js(path):
#     return send_from_directory('static/static/js', path)
#
#
# @app.route('/static/css/<path:path>')
# def send_css(path):
#     return send_from_directory('static/static/css', path)
#
#
# @app.route('/static/media/<path:path>')
# def send_media(path):
#     return send_from_directory('static/static/media', path)
#
#
# @app.route('/')
# def hello_world():
#     return app.send_static_file('index.html')


def map_res_pol(x):
    return {"name": x["name"].encode("utf-8").decode("utf-8"),
            "desc": list(map(lambda d: d.encode("utf-8").decode("utf-8"), x["desc"]))}


def map_res_word(x):
    return {"name": x["name"].encode("utf-8").decode("utf-8"),
            "desc": x["desc"].encode("utf-8").decode("utf-8"), "pos": x["pos"]}


def map_suggestions(x):
    return x["name"].encode("utf-8").decode("utf-8")


@app.route("/suggestions/<suggestion_path>", methods=["GET"])
def get_suggestions(suggestion_path):
    query = {"name": {"$regex": "^" + suggestion_path}}
    wordnet = [map_suggestions(x) for x in collection.find(query).limit(10)]
    polnet = [map_suggestions(x) for x in collectionPolnet.find(query).limit(10)]
    return make_response(jsonify(list(set(wordnet + polnet))), 200)


@app.route("/entries/<entry>", methods=["GET"])
def get_entry(entry):
    query = {"name": entry}
    wordnet = [map_res_word(x) for x in collection.find(query).limit(10)]
    polnet = [map_res_pol(x) for x in collectionPolnet.find(query).limit(10)]
    res = {}
    for entry in polnet:
        print(entry)
        if entry["name"] in res:
            res[entry["name"]]["desc"]["polnet"].append(entry["desc"])
        else:
            res[entry["name"]] = {"desc": {"polnet": [entry["desc"]], "wordnet": []}, "pos": ""}
    for entry in wordnet:
        print(entry)
        if entry["name"] in res:
            res[entry["name"]]["desc"]["wordnet"].append(entry["desc"])
            res[entry["name"]]["pos"] = entry["pos"]
        else:
            res[entry["name"]] = {"desc": {"wordnet": [entry["desc"]],"polnet":[]}, "pos": entry["pos"]}

    res_list = list(map(lambda item: {"name": item[0], "desc": item[1]["desc"], "pos": item[1]["pos"]}, res.items()))
    return make_response(jsonify(res_list), 200)


if __name__ == '__main__':
    app.run()
