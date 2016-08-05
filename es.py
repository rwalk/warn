import logging

import elasticsearch
from data.demo import EVENTS
from data.locations import LOC_SYNONYMS
from schema import validate_event

LOG = logging.getLogger(__name__)

class WarnSearch():
    def __init__(self):
        self.es = elasticsearch.Elasticsearch()

    @staticmethod
    def filter_dict(data):
        """drop out keys and values that we don't want to pass to elasticsearch"""
        return {k: v for k, v in data.items() if v is not None and k != "id"}

    def _do_search(self, query):
        body = self.es.search("events", "event", query)
        return body["hits"]["hits"], body["hits"]["total"]

    def find_events(self, company, location, limit=10, offset=0, sort_by="relevance"):
        '''
        Find events based on parameters passed by user
        :param company:
        :param location:
        :param limit:
        :param offset:
        :param sort_by:
        :return: array of elasticsearch hits
        '''

        # Query construction/arg parsing
        query = {
            "query": {
                "bool": {}
            },
            "size": limit,
            "from": offset
        }
        bquery = query["query"]["bool"]

        if location is None and company is None:
            query["query"] = {"match_all": {}}

        if company:
            bquery["must"] = [{"match": {"company": company}}]
        if location:
            bquery["should"] = [{"match": {"location": location}}]
        if sort_by == "date":
            query["sort"] = [{"effective-date": {"order": "desc"}}, "_score"]

        # execute the search
        import json
        print(json.dumps(query, indent=2))
        return self._do_search(query)

    def add_event(self, event):
        if validate_event(event):
            self.es.index("events", "event", self.filter_dict(event), id=event["id"])
        else:
            raise RuntimeError("Event %s is not valid!" % str(event))

    def get_event(self, _id):
        return self.es.get("events",_id, doc_type="event")

class SearchControl():
    @staticmethod
    def populate():
        '''populate index with some test data'''
        ES = WarnSearch()
        for event in EVENTS:
            ES.add_event(event)

    @staticmethod
    def destroy():
        ES = elasticsearch.Elasticsearch()
        ES.indices.delete("events", ignore=404)

    @staticmethod
    def create():
        ES = elasticsearch.Elasticsearch()
        ES.indices.create("events", {
            "settings": {
                "analysis": {
                    "filter": {
                        "location_synonyms_filter": {
                            "type": "synonym",
                            "synonyms": LOC_SYNONYMS
                        }
                    },
                    "analyzer": {
                        "location_analyzer": {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "location_synonyms_filter"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "event": {
                    "properties": {
                        "company": {
                            "type": "string",
                            "index": "analyzed"
                        },
                        "number-affected": {
                            "type": "integer",
                        },
                        "effective-date": {
                            "type": "date"
                        },
                        "notice-date": {
                            "type": "date"
                        },
                        "state": {
                            "type": "string",
                            "index": "not_analyzed",
                            "copy_to": "location"
                        },
                        "county": {
                            "type": "string",
                            "copy_to": "location"
                        },
                        "city": {
                            "type": "string",
                            "copy_to": "location"
                        },
                        "notes": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "location": {
                            "type": "string",
                            "analyzer": "location_analyzer"
                        },
                        "source": {
                            "type": "object",
                            "properties": {
                                "name": { "type": "string", "index": "not_analyzed"},
                                "url": { "type": "string", "index": "not_analyzed"}
                            }
                        }
                    }
                }
            }
        }, ignore=400)
