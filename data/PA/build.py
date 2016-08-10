#!/usr/bin/env python
import csv, re, requests, argparse
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from time import sleep
from random import randint, shuffle
from data.utils import derived_id, format_date, DateParserError
from dateutil import rrule
import os
import traceback
from es import WarnSearch

basepath = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(basepath, "data")

BASE_URL = "http://www.dli.pa.gov/Individuals/Workforce-Development/warn/notices/Pages/"
NUMS_RE = re.compile("\d+")
CITY_STATE_RE = re.compile(r".*, PA( \d{5})?")
DATE_RE = re.compile("\d{1,2}/\d{1,2}/\d{2,4}")


def scrub(text):
    txt = re.sub(r"\n+", "\n", text)
    txt = re.sub(r"[\r\xa0]", "", txt)
    txt = re.sub(r" +"," ", txt)
    txt = re.sub(r"\n+", "\n", txt)
    return(txt)

COUNTER = {
    "fail":0,
    "success":0
}

def process_file(fname):
    with open(fname) as f:
        data = f.read()
        soup = BeautifulSoup(data, "lxml")
        table = soup.findAll('table')[2]
        basename = os.path.splitext(os.path.basename(fname))[0]
        filedate = datetime.strftime(datetime.strptime(basename, "%B-%Y").date(), '%Y-%m-%d')
        ES = WarnSearch()
        for row in table.findAll("td"):
            if row.text.strip()!="":
                try:
                    notes = []

                    # we punt on cases with multiple counties for now
                    if 'COUNTIES:' in row.text:
                        raise RuntimeError("Multi-counties not supported")

                    # is this an update to a previous record?
                    if 'UPDATE' in row.text:
                        notes.append("Record is an UPDATE to a previous record.")

                    # handle the strange way updates are input
                    company = row.findAll("strong")[0].text.split("\n")
                    if len(company)>1:
                        company=company[1].strip()
                    else:
                        company=company[0].strip()

                    # extract geo
                    lines = row.text.split("\n")
                    city = None
                    for line in lines:
                        if CITY_STATE_RE.match(line.strip()):
                            tokens = line.strip().split(",")
                            if len(tokens)==2:
                                city = tokens[0]

                    # extract county, date, number affected
                    county = None
                    employees = None
                    effective=None

                    cells = [row.strip() for row in scrub(row.text).split("\n") if len(row.strip())>0]

                    for txt in cells:
                        if 'COUNTY:' in txt or 'COUNTIES:' in txt:
                            county=txt.split(":")[1]
                        elif "# AFFECTED" in txt:
                            valtxt = txt.split(":")[1].strip()
                            number_txt = valtxt.replace(",","")
                            values = [int(v) for v in re.findall(NUMS_RE, number_txt)]
                            if len(values)==0:
                                employees=0
                                notes.append("Number affected listed as '%s'" % valtxt)
                            else:
                                if len(values)>1:
                                    notes.append("Number affected employees listed as '%s'" % valtxt)
                                employees = values[0]
                        elif "EFFECTIVE DATE" in txt:
                            datetxt = txt.split(':')[1].strip()
                            edates = DATE_RE.findall(datetxt)
                            if len(edates)==1:
                                effective = format_date(edates[0])
                            elif len(edates)>1:
                                effective = format_date(edates[0])
                                notes.append("Effective date listed as '%s.'" % datetxt)
                            else:
                                effective = filedate
                                notes.append("Effective date listed as '%s.'" % datetxt)
                                notes.append("Notice publication date used as effective date.")


                    if None in [county, employees, effective]:
                        print("BUSTED: %s" % row)
                        print(company, effective, county)
                        raise RuntimeError("Bad parse: %s" % str([county, employees, effective]))

                    event = {
                        "id": derived_id(company, employees, effective, "PA", city),
                        "company": company,
                        "number-affected": employees,
                        "county":county,
                        "state": "PA",
                        "effective-date": effective,
                        "source": {
                            "name": "Pennsylvania Department of Labor & Industry",
                            "url": "http://www.dli.pa.gov/Individuals/Workforce-Development/warn/notices/Pages/default.aspx"
                        }
                    }
                    if city:
                        event["city"] = city
                    if len(notes)>0:
                        event["notes"] = "; ".join(notes)
                    print(json.dumps(event, sort_keys=True, indent=2))
                    ES.add_event(event)
                    COUNTER["success"]+=1
                except (DateParserError, IndexError, RuntimeError) as e:
                    COUNTER["fail"]+=1
                    print("\n\n" + "%"*79)
                    print(e)
                    traceback.print_exc()
                    print("WARNING: FAILED TO PROCESS: %s" % row.text)

def fetch_data(dates, outdir=DATADIR):
    if len(dates) == 1:
        start_date = datetime.strptime(dates[0], '%m-%Y').date()
        end_date = start_date
    elif len(dates) == 2:
        start_date = datetime.strptime(dates[0], '%m-%Y').date()
        end_date = datetime.strptime(dates[1], '%m-%Y').date()
    else:
        raise RuntimeError("Either a date or both a start and end date (MM-YYYY) must be provided!")

    daterange = ([dt.strftime("%B-%Y") for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date)])
    shuffle(daterange)
    total = len(daterange)
    done = 0
    for dt in daterange:
        filename = dt + ".aspx"
        url = BASE_URL+filename
        print("Working on " + filename)
        r = requests.get(url)
        if r.status_code == 200:
            with open(os.path.join(outdir, dt + ".html"), "w") as f:
                f.write(r.text)
        else:
            print("Bad request. " + str(r))
        done+=1
        if done<total:
            waittime = 1 + randint(15,30)
            print("Waiting %d seconds before next request." % waittime)
            sleep(waittime)

def build_archive():
    for fname in os.listdir(DATADIR):
        print("Working on file %s." % fname)
        process_file(os.path.join(DATADIR, fname))

def build_latest():
    dt = datetime.now()
    mmyy = dt.strftime("%m-%Y")
    fetch_data([mmyy], outdir="/tmp")
    process_file(os.path.join("/tmp", os.path.join("/tmp", dt.strftime("%B-%Y") + ".html")))

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process PA warn reports.')
    parser.add_argument('date', type=str, nargs='+', help='MM-YYYY start and end date or single date')
    args = parser.parse_args()
    build_archive()
    build_latest()
    print(COUNTER)