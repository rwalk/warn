import os
import csv
import json

from ..utils import derived_id
from es import WarnSearch
from datetime import datetime

basepath = os.path.dirname(os.path.abspath(__file__))
valid = {
            "id": "b9fb701b3578d39811844a11de3c58a6",
            "company": "Dunder Mifflin, Inc.",
            "number-affected": 63,
            "effective-date" : "May 16th, 2013",
            "state": "PA",
            "county": "Lacawanna",
            "city": "Scranton",
            "notes": "closed after 13 seasons",
            "source": "PAWARNnotices2013.xls"
        }

def format_date(datestr):
    tokens = datestr.split("/")
    if len(tokens[2])==2:
        if int(tokens[2])<20:
            yy = "20" + tokens[2]
        else:
            yy = "19" + tokens[2]
    else:
        yy = tokens[2]
    datestr = "/".join(tokens[0:2] + [yy])
    old = datetime.strptime(datestr,'%m/%d/%Y')
    return old.strftime('%Y-%m-%d')

def main():
    ES = WarnSearch()

    for fname in os.listdir(os.path.join(basepath, "data")):
        with open(os.path.join(basepath,"data",fname)) as f:


            reader = csv.reader(f, delimiter="|")
            header = next(reader)
            for line in reader:
                data = {k:v for k,v in zip(header,line)}
                print("INP: \n" + json.dumps(data, indent=2))
                event = {
                    "company": (data.get("name") or data.get("company")).title(),
                    "number-affected":int(data["employees"]),
                    "effective-date":format_date(data["effective"]),
                    "state":"CA",
                    "source": {
                        "name":"CA Employment Development Division",
                        "url":"http://www.edd.ca.gov/Jobs_and_Training/Layoff_Services_WARN.htm#ListingofWARNNotices"
                    }
                }
                if not data.get("id"):
                    uid = derived_id(event["company"], event["number-affected"], event["effective-date"], event["state"])
                    event["id"] = uid
                else:
                    event["id"] = data["id"]

                # location handler
                if "city" in data:
                    event["city"] = data["city"].title()
                elif "location" in data:
                    event["city"] = data["location"].title()

                # date handler
                if "notice" in data:
                    event["notice-date"] = format_date(data["notice"])
                elif "received" in data or "recieved" in data:
                    print(data)
                    event["notice-date"] = format_date(data.get("received") or data.get("recieved"))

                # compact out any nulls
                event = {k: v for k, v in event.items() if v is not None}
                print("OUT: \n" + json.dumps(event, indent=2))
                ES.add_event(event)