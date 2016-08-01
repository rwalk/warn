from es import WarnSearch, SearchControl
from unittest import TestCase
from data.demo import EVENTS
from time import sleep

class TestWarnES(TestCase):

    def setUp(self):
        SearchControl.destroy()
        SearchControl.create()

    def tearDown(self):
        SearchControl.destroy()

    def test_add_event(self):
        ES = WarnSearch()
        ES.add_event(EVENTS[0])
        _id = EVENTS[0]["id"]
        result = ES.get_event(_id)
        self.assertEqual(EVENTS[0]["id"], result["_id"])
        self.assertEqual(EVENTS[0]["company"], result["_source"]["company"])

    def test_search_event_by_company(self):
        SearchControl.populate()
        sleep(2)
        es = WarnSearch()
        events = es.find_events("dunder mifflin inc", None)
        self.assertEqual("Dunder Mifflin, Inc.", events[0]["_source"]["company"])

    def test_search_event_by_location(self):
        SearchControl.populate()
        sleep(2)
        es = WarnSearch()
        events = es.find_events(None, "New York City")
        self.assertEqual(4, len(events))
        self.assertEqual("Dunder Mifflin/Sabre Corporate HQ", events[0]["_source"]["company"])

    def test_search_company_and_location(self):
        SearchControl.populate()
        sleep(2)
        es = WarnSearch()
        events = es.find_events("Sabre", "florida")
        self.assertEqual("Sabre Printers and Office Supplies", events[0]["_source"]["company"])