#!/usr/bin/env python
import os
import re
import xlrd
import requests
import json
import datetime
from es import WarnSearch
from data.utils import derived_id, format_date

basepath = os.path.dirname(os.path.abspath(__file__))

DATADIR = os.path.join(basepath, "data")
SEP_RE = re.compile(" {3,}")

def xl2date(xl):
    if type(xl) == float:
        return datetime.datetime(*xlrd.xldate_as_tuple(xl, 0)).strftime("%m/%d/%Y")


def process_file(fname, dry_run=False):
    book = xlrd.open_workbook(fname)
    sh = book.sheet_by_index(0)
    cnt = 0
    ES = WarnSearch()
    for rx in range(1, sh.nrows):
        row = sh.row_values(rx)

        # skip all empty row
        if all([type(r) == str and r == "" for r in row]):
            continue

        print("IN: " + str(row))
        cnt+=1

        notice_date = xl2date(row[0])
        company = row[1]
        county = row[2]
        district = row[3]
        received = xl2date(row[6])
        city = row[7]

        notes = []
        try:
            employees = "%d" % row[4]
        except TypeError:
            employees = "0"
            notes.append("Number affected employees listed as '%s'." % row[4])

        effective = xl2date(row[5])
        if effective is None:
            notes.append("Effective date not provided. Using date of receipt as effective date.")
            effective = received

        event = {
            "company": company,
            "number-affected":int(employees),
            "effective-date":format_date(effective),
            "city": city,
            "county": county,
            "state":"TX",
            "source": {
                "name":"Texas Workforce Commission",
                "url":"http://www.twc.state.tx.us/businesses/worker-adjustment-and-retraining-notification-warn-notices#warnNotices"
            }
        }

        if notice_date != None:
            event["notice-date"] = format_date(notice_date)

        if len(notes)>0:
            event["notes"] = "  ".join(notes)

        # ids
        event["id"] = derived_id(event["company"], event["number-affected"], event["effective-date"], event["state"], event["city"], event["county"])

        # compact out any nulls
        event = {k: v for k, v in event.items() if v is not None}
        print("OUT: \n" + json.dumps(event, indent=2))
        ES.add_event(event)
    print("PROCESSED: %d rows in FILE: %s" % (cnt, fname))

def build_archive():
    for fname in os.listdir(DATADIR):
        print("Working on file %s." % fname)
        process_file(os.path.join(DATADIR, fname))

def build_latest():
    # Retrieve the latest report
    BASE_URL = "http://www.twc.state.tx.us/files/news/"
    current_year = datetime.date.strftime(datetime.date.today(), "%Y")
    fname = "warn-act-listings-%s.xlsx" % current_year
    url = BASE_URL+fname
    print("Downloading %s" % url )
    r = requests.get(url)
    with open(os.path.join("/tmp", fname), "wb") as code:
        code.write(r.content)

    # call processor on latest report
    process_file(os.path.join("/tmp", fname))

if __name__ == "__main__":
    build_archive()
    build_latest()