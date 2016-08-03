import argparse
from flask import Flask, render_template, request, flash, g, abort, jsonify
from db import WarnDB
from schema import validate_event
from es import WarnSearch, SearchControl

app = Flask(__name__)
ES = WarnSearch()
MAX_RESULTS = 10

def add_location_string(data):
    for element in data:
        row = element["_source"]
        state  = row["state"]
        county = row.get("county")
        if county and not county.endswith("County"):
            county = county + " County"
        city = row.get("city")
        row["location"] = ", ".join([_ for _ in [city, county, state] if _ is not None])

@app.route("/")
def home():
    page = int(request.args.get("page", 1))
    data,total = ES.find_events(None, None, MAX_RESULTS, (page-1)*MAX_RESULTS, "date")
    add_location_string(data)
    results = [row["_source"] for row in data]
    print(total)
    print(total//MAX_RESULTS+1)

    return render_template("index.html", hits=results,
                           total_results=total,
                           current_page=page,
                           number_pages=total//MAX_RESULTS + 1)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/dash")
def dash():
    return render_template("dash.html")

@app.route("/data")
def data():
    return render_template("data.html")


@app.route("/search", methods=["GET"])
def handle_events():
    company = request.args.get("company_search")
    location = request.args.get("location_search")
    sort_by = request.args.get("sort", "relevance")
    page = int(request.args.get('page',1))

    if company is None and location is None:
        return home()
    data, total = ES.find_events(company, location, 10, (page-1)*10, sort_by)
    add_location_string(data)
    results = [row["_source"] for row in data]
    query_string = ", ".join([_ for _ in [company,location] if _ is not None and len(_)>0])


    return render_template("index.html", hits=results,
                           total_results=total,
                           query=query_string,
                           current_page=page,
                           number_pages=total//MAX_RESULTS + 1)

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