#!/usr/bin/env python
import argparse
from es import SearchControl
from time import sleep
from data.CA.build_index import main as CA_main
from data.TX.build import build_archive as TX_archive, build_latest as TX_latest
from data.FL.build import build_archive as FL_archive, build_latest as FL_latest
from data.PA.build import build_archive as PA_archive, build_latest as PA_lastest

PROCESSOR_MAP = {
    "CA": [CA_main],
    "TX": [TX_archive, TX_latest],
    "FL": [FL_archive, FL_latest],
    "PA": [PA_archive, PA_lastest]
}


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Execute state warn report parsers")
    parser.add_argument("state", nargs="*", help="Two letter state code to process, one of %s." % ", ".join(PROCESSOR_MAP.keys()))
    parser.add_argument("-d", "--destroy", action="store_true", help="Tear down and rebuild the existing elasticsearch index.")
    args = parser.parse_args()

    # tear down and recreate ES index
    if args.destroy:
        ES = SearchControl()
        ES.destroy()
        sleep(2)
        ES.create()
        sleep(2)

    # populate index
    for state in args.state:
        if state not in PROCESSOR_MAP:
            print("%s is not a valid state code.  Choose one of %s" % (state, ", ".join(PROCESSOR_MAP.keys())))
        for processor in PROCESSOR_MAP["FL"]:
            processor()
