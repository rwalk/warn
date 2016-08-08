#!/usr/bin/env python
from es import SearchControl
from data.CA.build_index import main as CA_main
from data.TX.build import build_archive as TX_archive, build_latest as TX_latest
from time import sleep


if __name__ == "__main__":

    # tear down and recreate ES index
    ES = SearchControl()
    ES.destroy()
    sleep(2)
    ES.create()
    sleep(2)

    # populate index
    TX_archive()
    TX_latest()
    CA_main()
