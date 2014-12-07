#!/usr/bin/env python3

UW_API_KEY = "123afda14d0a233ecb585591a95e0339"
UW_API_BASE = "http://api.uwaterloo.ca/v2/"

import time

import requests

cached_responses = {} # the cached responses of each request
cache_expiry = 60 * 60 * 24 * 7 # cache expiry duration in seconds

def uwapi(endpoint, params={}):
    try:
        if endpoint in cached_responses and time.time() - cached_responses[endpoint]["meta"]["timestamp"] < cache_expiry: # check if requested endpoint is cached and didn't expire
            print("retrieving", endpoint)
            return cached_responses[endpoint]["data"]
    except KeyError: pass # catch any KeyError instances upon invalid data
    print("querying", endpoint)
    params["key"] = UW_API_KEY
    r = requests.get(UW_API_BASE + endpoint + ".json", params=params)
    assert r.status_code == 200
    value = r.json()
    cached_responses[endpoint] = value # update cache
    return value["data"]
