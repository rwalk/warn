from es import WarnSearch, SearchControl
from unittest import TestCase
from data import EVENTS

class TestWarnES(TestCase):

    def setUp(self):
        SearchControl.create()

    def tearDown(self):
        SearchControl.destroy()

    def test_add_event(self):
        ES = WarnSearch()
        ES.add_event(EVENTS[0])
        _id = EVENTS[0]["id"]
        result = ES.get_event(_id)
        self.assertEqual(EVENTS[0]["id"], result["_id"])
        self.assertEqual(EVENTS[0]["_source"]["company"], result["company"])

    def test_search_event_by_company(self):
        SearchControl.populate()
        es = WarnSearch()
        events = es.find_events("dunder mifflin inc", None)
        self.assertGreaterEqual(1, len(events))
        self.assertEqual("Dunder Mifflin, Inc.", events[0]["_source"]["company"])