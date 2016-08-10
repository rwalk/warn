import hashlib
import re
import os
import subprocess
import tempfile
import requests
import uuid
from datetime import datetime
import traceback

SALT_PHRASE = "fad23423fsdfahl227&qqqed&&&&&&1111232345"

class DateParserError(Exception):
    pass

def derived_id(*values):
    """compute an id"""
    if len(values)<1:
        raise RuntimeError("Can't construct derived ID; no fields provided")
    did = "".join([str(v) for v in values]) + SALT_PHRASE
    did = re.sub("\W", "", did).upper()
    did = hashlib.md5(did.encode()).hexdigest()
    return did

def text_from_pdf(content_url):
    r = requests.get(content_url)
    basename = uuid.uuid4().hex
    pdf_file = os.path.join("/tmp", basename + ".pdf")
    text_file = os.path.join("/tmp", basename + ".txt")

    with open(pdf_file, "wb") as f:
        f.write(r.content)

    ok = subprocess.call(["pdftotext", "-layout", "-nopgbrk", pdf_file, text_file])
    if ok!=0:
        raise RuntimeError("Couldn't convert that PDF.")
    else:
        print("Extracted PDF text to file: %s" % text_file)
        return text_file

def format_date(datestr):
    try:
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
    except (IndexError, ValueError):
        print("UNPARSABLE DATE STRING: %s" % datestr)
        print(traceback.print_exc())
        raise DateParserError


if __name__ == "__main__":
    text_from_pdf("http://www.edd.ca.gov/Jobs_and_Training/warn/WARN-Report-for-7-1-2015-to-06-30-2016.pdf")
