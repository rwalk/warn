import os
import csv
import json

from ..utils import derived_id
from es import WarnSearch
from data.utils import format_date

basepath = os.path.dirname(os.path.abspath(__file__))

def main():
    ES = WarnSearch()


    # process archived data.
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

    # process latest data
