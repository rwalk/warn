from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
import logging
import hashlib
from time import mktime
import datetime

LOG = logging.getLogger(__name__)

def LayoffEvent(id, date, company, number_affected, location, notes):
    data = {
        "id": id,
        "company": company,
        "number-affected":number_affected,
        "location": location,
        "effective-date": mktime(datetime.datetime.strptime(date, '%Y-%m-%d').timetuple())
    }
    if notes:
        data["notes"] = notes
    return data

def Location(id,name,state,region,county,city):
    data = {
        "id": id,
        "name": name,
        "state": state,
        "aliases": [name]
    }
    if region:
        data["region"]=region
    if county:
        data["county"]=county
    if city:
        data["city"]=city
    return data

def Company(id, name):
    return {"id": id, "name":name, "aliases":[name]}

class WarnDB():

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.companies = client.companies
        self.events = client.events
        self.locations = client.locations

    def add_event(self, eid, date, company_id, number_affected, location_id, notes=None):
        cmp = self.get_company(company_id)
        loc = self.get_location(location_id)
        if cmp is None or loc is None:
            raise KeyError("Either company or location is not registered!")
        self.events.collection.insert_one(LayoffEvent(eid, date, company_id, number_affected, location_id, notes))

    def get_event(self, eid):
        return self.events.collection.find_one({"id": eid})

    def add_location(self, id, name, state, region=None, county=None, city=None):
        loc = Location(id, name, state, region, county, city)
        self.locations.collection.insert_one(loc)

    def add_location_alias(self, locid, alias):
        loc = self.get_location(locid)
        if alias not in loc["aliases"]:
            self.locations.collection.update({"id": locid}, {"$push": {"aliases":alias}})

    def get_location(self, locid):
        return self.locations.collection.find_one({"id": locid})

    def add_company(self, cid, name):
        cmp = Company(cid, name)
        self.companies.collection.insert_one(cmp)

    def add_company_alias(self, cid, alias):
        cmp = self.get_company(cid)
        if alias not in cmp["aliases"]:
            self.companies.collection.update({"id": cid}, {"$push": {"aliases":alias}})

    def get_company(self, cid):
        return self.companies.collection.find_one( {"id": cid } )

class DBControl:

    @staticmethod
    def destroy():
        client = MongoClient('localhost', 27017)
        dbs = client.database_names()
        for db in dbs:
            LOG.info("Droppin db %s..." % db)
            client.drop_database(db)