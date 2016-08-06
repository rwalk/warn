from data.warn_data_config import CONFIG
from data.utils import text_from_pdf
import re
import os
import csv
SEP_RE = re.compile(r"\s{2,}")

basepath = os.path.dirname(os.path.abspath(__file__))

def main():
    url = CONFIG["CA"]["latest-url"]
    txtfile = text_from_pdf(url)
    go = input("Update the file %s.  Then press any key to continue" % txtfile)
    with open(os.path.join(basepath, "data", "latest.csv"), "w") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(["notice","effective", "recieved","company","city","employees", "kind"])
        with open(txtfile) as f:
            header = SEP_RE.split(next(f))
            for line in f:
                data = {k.strip():v.strip() for k,v in zip(header,SEP_RE.split(line))}
                if len(list(data.values()))!=7:
                    raise RuntimeError("Bad record found;\n%s" % line)

                writer.writerow([
                 data["notice"],
                 data["effective"],
                 data["received"],
                 data["company"],
                 data["city"],
                 int(data["employees"]),
                 data["kind"]
                ])

if __name__ == "__main__":
    main()