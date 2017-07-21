#!/usr/bin/env python3

UW_API_KEY = "123afda14d0a233ecb585591a95e0339"
UW_API_BASE = "http://api.uwaterloo.ca/v2/"

import cachetools
import requests

@cachetools.cached(cachetools.TTLCache(maxsize=500, ttl=60 * 60 * 24)) # max 500 items, expire after a day
def uwapi(endpoint, **params):
    params["key"] = UW_API_KEY
    r = requests.get(UW_API_BASE + endpoint + ".json", params=params)
    assert r.status_code == 200, "HTTP error {}".format(r.status_code)
    value = r.json()
    return value["data"]

if __name__ == "__main__":
    print(uwapi("terms/list"))