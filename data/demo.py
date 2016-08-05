EVENTS = [
    {
        "id": "E1",
        "company": "Dunder Mifflin",
        "state": "PA",
        "city": "Scranton",
        "county": "Lackawanna",
        "effective-date": "2013-05-16",
        "number-affected": 25,
        "notes": "Series ended"
    },
    {
        "id": "E2",
        "company": "Prince Family Paper",
        "state": "PA",
        "city": "Scranton",
        "county": "Lackawanna",
        "effective-date": "2011-01-15",
        "number-affected": 15,
        "notes": "Victim of corporate espionage!"
    },
    {
        "id": "E3",
        "company": "Dunder Mifflin, Inc.",
        "state": "CT",
        "city": "Stamford",
        "effective-date": "2010-04-01",
        "number-affected": 30,
        "notes": "Some employees transford to Scranton branch"
    },
    {
        "id": "E4",
        "company": "Michael Scott Paper Company",
        "state": "PA",
        "city": "Scranton",
        "effective-date": "2011-04-01",
        "number-affected": 4,
        "notes": "Merged with Dunder Mifflin Inc"
    },
    {
        "id": "E5",
        "company": "Dunder Mifflin of Buffalo, Inc.",
        "state": "NY",
        "city": "Buffalo",
        "effective-date": "2012-05-16",
        "number-affected": 55,
    },
    {
        "id": "E6",
        "company": "Dunder Mifflin--Utica",
        "state": "NY",
        "city": "Utica",
        "county": "Oneida County",
        "effective-date": "2013-01-22",
        "number-affected": 75,
    },
    {
        "id": "E7",
        "company": "Dunder Mifflin/Sabre",
        "state": "NH",
        "city": "Nashua",
        "effective-date": "2013-04-01",
        "number-affected": 75,
    },
    {
        "id": "E8",
        "company": "Dunder Mifflin/Sabre Corporate HQ",
        "state": "NY",
        "city": "New York",
        "effective-date": "2013-05-01",
        "number-affected": 500,
    },
    {
        "id": "E9",
        "company": "Dunder Mifflin",
        "state": "OH",
        "city": "Akron",
        "effective-date": "2013-05-01",
        "number-affected": 200,
    },
    {
        "id": "E10",
        "company": "Sabre Printers and Office Supplies",
        "state": "FL",
        "city": "Jacksonville",
        "effective-date": "2013-05-01",
        "number-affected": 200,
    },
    {
        "id": "E11",
        "company": "Sabre Store",
        "state": "FL",
        "city": "Tallahasse",
        "effective-date": "2012-09-01",
        "number-affected": 15,
    },
    {
        "id": "E12",
        "company": "Vance Refridgeration",
        "state": "PA",
        "city": "Scranton",
        "effective-date": "2013-09-01",
        "number-affected": 15,
    },
    {
        "id": "E13",
        "company": "Dunder Mifflin",
        "state": "PA",
        "city": "Scranton",
        "effective-date": "2007-10-31",
        "number-affected": 1,
    },
    {
        "id": "E14",
        "company": "Serenity By Jan",
        "state": "PA",
        "city": "Scranton",
        "effective-date": "2010-10-31",
        "number-affected": 1,
    },
    {
        "id": "E15",
        "company": "Athlead",
        "state": "PA",
        "city": "Scranton",
        "effective-date": "2013-05-31",
        "number-affected": 15,
    },
    {
        "id": "E16",
        "company": "Big Red Paper Company",
        "state": "NY",
        "city": "Cornell",
        "effective-date": "2013-05-31",
        "number-affected": 1,
    },

]

for event in EVENTS:
    event["source"] = {
        "name": "NBC Universal",
        "url": "http://www.nbc.com/the-office"
    }