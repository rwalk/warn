from jsonschema import validate, ValidationError

events_schema = {
    "type": "object",
    "properties": {

        "id": {"type": "string"},
        "company": {"type": "string"},
        "number-affected": {"type": "number"},
        "effective-date": {"type": "string"},
        "notice-date": { "type": "string"},
        "state": { "type": "string" },
        "county": {"type": "string"},
        "city": {"type": "string"},
        "notes": {"type": "string"},
        "source": {"type":"object",
                    "properties": {
                        "name": {"type": "string"},
                        "url": {"type": "string"}
                    },
                   "additionalProperties": False,
                   "required": ["name", "url"]
                   },
    },
    "additionalProperties": False,
    "required": ["id", "company", "number-affected", "effective-date", "state", "source"]
}

def validate_event(event):
    try:
        validate(event, events_schema)
        return True
    except ValidationError:
        return False


if __name__ == "__main__":
    valid = {
                "id": "b9fb701b3578d39811844a11de3c58a6",
                "company": "Dunder Mifflin, Inc.",
                "number-affected": 63,
                "effective-date" : "May 16th, 2013",
                "state": "PA",
                "county": "Lacawanna",
                "city": "Scranton",
                "notes": "closed after 13 seasons",
                "source": {
                    "name": "duckduckgo",
                    "url": "www.duckduckgo.com"
                }
            }
    print("Testing VALID case: is valid? %s " % validate_event(valid))
    print("Testing INVALID case: is valid? %s " % validate_event({"hello":123}))