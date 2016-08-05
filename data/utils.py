import hashlib
import re

SALT_PHRASE = "fad23423fsdfahl227&qqqed&&&&&&1111232345"

def derived_id(*values):
    """compute an id"""
    if len(values)<1:
        raise RuntimeError("Can't construct derived ID; no fields provided")
    did = "".join([str(v) for v in values]) + SALT_PHRASE
    did = re.sub("\W", "", did).upper()
    did = hashlib.md5(did.encode()).hexdigest()
    return did