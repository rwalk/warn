import argparse
from flask import Flask, render_template, request, flash, g, abort, jsonify
from db import WarnDB
from schema import validate_event
from es import WarnSearch, SearchControl

app = Flask(__name__)
ES = WarnSearch()

@app.route("/events", methods=["POST", "GET"])
def handle_events():
    if request.method=="POST":
        if not request.json or not validate_event(request.json):
            abort(400)
        ES.add_event(request.json)
    elif request.method == "GET":
        company = request.args.get("company")
        location = request.args.get("location")
        sort_by = request.args.get("sort", "relevance")
        limit = request.args.get("limit",10)
        offset = request.args.get("offset",0)
        return jsonify(ES.find_events(company, location, limit, offset, sort_by)), 200

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Open doxie warn Server.")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("-p", "--port", default=5000, type=int)

    args = parser.parse_args()

    SearchControl.destroy()
    SearchControl.create()
    SearchControl.populate()

    # launch ECD!
    app.run(host='0.0.0.0', debug=args.debug, port=args.port, threaded=True)