#!/usr/bin/env python3

UW_API_KEY = "123afda14d0a233ecb585591a95e0339"
UW_API_BASE = "http://api.uwaterloo.ca/v2/"

import requests

cached_responses = {} # the cached responses of each request
def uwapi(endpoint, params={}):
    try:
        if endpoint in cached_responses: # check if requested endpoint is cached
            print("retrieving", endpoint)
            return cached_responses[endpoint]
    except KeyError: pass # catch any KeyError instances upon invalid data
    print("querying", endpoint)
    params["key"] = UW_API_KEY
    r = requests.get(UW_API_BASE + endpoint + ".json", params=params)
    assert r.status_code == 200
    value = r.json()
    cached_responses[endpoint] = value["data"] # update cache
    return value["data"]
