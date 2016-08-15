import os
import re
import json
from data.utils import derived_id, format_date, text_from_pdf
from datetime import datetime, date, timedelta
import requests
from random import randint, shuffle
from dateutil import rrule
from time import sleep
from es import WarnSearch

SEP_RE = re.compile("\s{3,}")
FIELD_RE = re.compile(r"[A-Z,\&\# ]+:\t[\S ]+")
FOOT_RE = re.compile(" {3,}Supplementals")

basepath = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(basepath, "data")
DATE_RE = re.compile("\d{1,2}/\d{1,2}/\d{4}")
NUMS_RE = re.compile("\d+")

#BASE_URL = "http://www2.illinoisworknet.com/DownloadPrint/July%202016%20Monthly%20WARN%20Report.pdf"
BASE_URL = "http://www2.illinoisworknet.com/DownloadPrint/"
FILEMASK = "%s Monthly WARN Report"

def get_fields(text):
    field_map = {}
    text = re.sub(" {3,}", "\t", text.replace("\t", "    "))
    for field in re.findall(FIELD_RE, text):
        fv = field.split(":\t")
        name = re.sub("[\#\&,]", "", fv[0]).lower().strip().replace(" ", "_").replace("__", "_")
        # re can't match a field without a value, so we should always have len(fv)==2
        field_map[name] = fv[1]
    if "city_state" in field_map and "city_state_zip" not in field_map:
        field_map["city_state_zip"] = field_map["city_state"]
    return (field_map)


def process_file(fname):
    ES = WarnSearch()
    with open(fname, "r") as f:
        text = f.read()

        # remove header and footer
        start = text.find("COMPANY NAME:")
        end = FOOT_RE.search(text)
        if end is None:
            end = len(text)
        else:
            end = end.start() - 1
        text = text[start:end]
        entries = [cell.strip() for cell in text.split("COMPANY NAME:") if len(cell.strip())>0]

    for entry_txt in entries:

        # attempt to use tabs as field seperator instead of multiple spaces
        txt = SEP_RE.sub("\t", entry_txt)

        # normalize text
        txt = txt.strip()
        txt = txt.replace("Permanent or Temporary:", "PERMANENT OR TEMPORARY:")

        # extract fields and values
        field_map = get_fields(txt)

        # process recovered fields
        company = txt.split("\t")[0].strip()

        if not "TYPE OF EVENT:" in company:
            notes = []

            # affected
            try:
                affected = int(field_map["workers_affected"])
            except ValueError:
                notes.append("Number affected listed as '%s'." % field_map["workers_affected"])
                parsed = NUMS_RE.findall(field_map["workers_affected"])
                if len(parsed)>0:
                    affected = int(parsed[0])
                else:
                    affected = 0
            city = field_map["city_state_zip"].split(",")[0].strip()
            try:
                notice = format_date(field_map["warn_notified_date"].replace("-", "/"))
            except:
                notice = None
                notes.append("Notice date not provided.")
            # date handling
            try:
                effective = format_date(field_map["first_layoff_date"].replace("-","/"))
            except:
                try:
                    effective = format_date(field_map["ending_layoff_date"].replace("-", "/"))
                except:
                    notes.append("Effective date not available; notice date used as effective date.")
                    effective = notice

            event = {
                "id": derived_id(company, affected, "IL", city, effective, notice),
                "company": company,
                "number-affected": affected,
                "city": city,
                "state": "IL",
                "effective-date": effective,
                "source": {
                    "name": "Illinois Dept. of Commerce and Economic Opportunity",
                    "url": "http://www2.illinoisworknet.com/LayoffRecovery/Pages/ArchivedWARNReports.aspx"
                }
            }
            if 'county' in field_map:
                event["county"] = field_map["county"]
            if len(notes)>0:
                event["notes"] = " ".join(notes)
            if notice:
                event["notice-date"]=notice
            print(json.dumps(event, sort_keys=True, indent=2))
            try:
                ES.add_event(event)
            except RuntimeError:
                print("INVALID EVENT: %s" % json.dumps(event, sort_keys=True, indent=2))
        else:
            print("BAD TEXT:\n%s" % txt.replace("\n", " "))

def build_archive():
    for fname in os.listdir(DATADIR):
        print("Working on file %s." % fname)
        process_file(os.path.join(DATADIR, fname))

def fetch_data(dates):
    if len(dates) == 1:
        start_date = datetime.strptime(dates[0], '%m-%Y').date()
        end_date = start_date
    elif len(dates) == 2:
        start_date = datetime.strptime(dates[0], '%m-%Y').date()
        end_date = datetime.strptime(dates[1], '%m-%Y').date()
    else:
        raise RuntimeError("Either a date or both a start and end date (MM-YYYY) must be provided!")

    daterange = ([dt.strftime("%B %Y") for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date)])
    shuffle(daterange)
    total = len(daterange)
    done = 0
    for dt in daterange:
        filename_base = FILEMASK % dt
        url = BASE_URL + filename_base + ".pdf"
        print("Fetching: %s" % url)
        with open(os.path.join(DATADIR, filename_base.replace(" ", "_") + ".txt"), "w") as f:
            with open(text_from_pdf(url), "r") as finput:
                f.write(finput.read())
        done+=1
        if done<total:
            waittime = 1 + randint(15,30)
            print("Waiting %d seconds before next request." % waittime)
            sleep(waittime)

def build_latest():
    latest = datetime.strftime(date.today().replace(day=1)-timedelta(days=1), "%m-%Y")
    latest_tag = datetime.strftime(date.today().replace(day=1)-timedelta(days=1), "%B_%Y")
    fetch_data([latest])
    process_file(os.path.join(DATADIR, (FILEMASK % latest_tag + ".txt").replace(" ", "_")))

if __name__ == "__main__":
    build_archive()
