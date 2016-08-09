import os
import re
import traceback
import datetime
import requests
from bs4 import BeautifulSoup
from es import WarnSearch
from data.utils import derived_id, format_date

basepath = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(basepath, "data")
DATE_RE = re.compile("\d{1,2}/\d{1,2}/\d{4}")

def process_file(fname):
    with open(fname, "r") as f:
        ES = WarnSearch()
        data = f.read()
        soup = BeautifulSoup(data, "lxml")
        table = soup.findAll('table')
        rows = table[0].findAll("tr")[2:]
        for row in rows:
            cols = row.findAll("td")
            # name and location
            fullname = cols[0].get_text("\n").split("\n")
            company = cols[0].findAll("font")[0].get_text(" ")
            address = fullname[1:]
            city = address[-1].split(",")[0]
            notice = format_date(cols[1].get_text(" "))
            notes = []

            effective = cols[2].get_text(" ")
            if effective is None or len(effective.strip())==0:
                effective=cols[1].get_text(" ")
                notes.append("Effective date not provided.  Assuming notice date is effective date.")

            if "thru" in effective:
                dates = DATE_RE.findall(effective)
                if len(dates)==2 and dates[0]!=dates[1]:
                    notes.append(effective)
            effective = format_date(DATE_RE.findall(effective)[0])


            event = {
                "company": company,
                "number-affected":int(cols[3].get_text(" ")),
                "effective-date": effective,
                "notice-date": notice,
                "city": city,
                "state": "FL",
                "source": {
                    "name": "Florida Department of Economic Opportunity",
                    "url": "http://www.floridajobs.org/office-directory/division-of-workforce-services/workforce-programs/reemployment-and-emergency-assistance-coordination-team-react/warn-notices"
                }
            }
            if len(notes)>0:
                event["notes"] = "; ".join(notes)
            event["id"] = derived_id(event["company"], event["number-affected"], event["effective-date"], event["state"], event["city"])
            print(event)
            ES.add_event(event)

def build_archive():
    for fname in os.listdir(DATADIR):
        print("Working on file %s." % fname)
        process_file(os.path.join(DATADIR, fname))

def build_latest():
    BASE_URL = "http://www.floridajobs.org/REACT/warn.asp?year=%s"
    current_year = datetime.date.strftime(datetime.date.today(), "%Y")
    url = BASE_URL % current_year
    print("Downloading %s" % url )
    r = requests.get(url)
    fname = "/tmp/fl_warn_%s.html" % current_year
    with open(fname, "w") as f:
        f.write(r.text)
    process_file(fname)

