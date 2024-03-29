import argparse
import datetime
import logging
from es import WarnSearch, SearchControl
from flask import Flask, render_template
from flask import request
from logger import WARNLogger
from werkzeug import url_encode

app = Flask(__name__)
app.logger.addHandler(WARNLogger.get_logstash_handler())
app.logger.setLevel(logging.INFO)

ES = WarnSearch()
MAX_RESULTS = 10
VISIBLE_WIDTH = 2


@app.before_request
def request_logging():
    if not "/static/" in request.url:
        app.logger.info('  '.join([
            request.remote_addr,
            request.method,
            request.url,', '.join([': '.join(x) for x in request.headers])]))


@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(request.path, url_encode(args))

@app.route("/")
def home():
    page = int(request.args.get("page", 1))
    data, total = ES.find_events(None, None, MAX_RESULTS, (page - 1) * MAX_RESULTS, "date")
    number_pages = total // MAX_RESULTS + 1 if total % MAX_RESULTS != 0 else total // MAX_RESULTS
    return render_template("index.html", hits=data,
                           total_results=total,
                           current_page=page,
                           number_pages=number_pages,
                           start_window=max(1, number_pages - 9),
                           end_window=min(page + 10, number_pages),
                           start_visible=max(1, page - VISIBLE_WIDTH),
                           end_visible=min(page + VISIBLE_WIDTH, number_pages)
                           )


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
    page = int(request.args.get('page', 1))

    if company is None and location is None:
        return home()
    data, total = ES.find_events(company, location, 10, (page - 1) * 10, sort_by)
    query_string = ", ".join([_ for _ in [company, location] if _ is not None and len(_) > 0])
    number_pages = total // MAX_RESULTS + 1 if total % MAX_RESULTS != 0 else total // MAX_RESULTS
    return render_template("index.html", hits=data,
                           total_results=total,
                           query=query_string,
                           current_page=page,
                           number_pages=number_pages,
                           start_window=max(1, number_pages - 9),
                           end_window=min(page + 10, number_pages),
                           start_visible=max(1, page - VISIBLE_WIDTH),
                           end_visible=min(page + VISIBLE_WIDTH, number_pages)
                           )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Open doxie warn Server.")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("-p", "--port", default=5000, type=int)

    args = parser.parse_args()

    # SearchControl.destroy()
    SearchControl.create()
    SearchControl.populate()

    # launch ECD!
    app.run(host='0.0.0.0', debug=args.debug, port=args.port, threaded=True)
