#!/usr/bin/env python3

UW_API_KEY = "PUT_YOUR_UW_API_KEY_HERE"
UW_API_BASE = "http://api.uwaterloo.ca/v2/"

import requests

def uwapi(endpoint, params={}):
    params["key"] = UW_API_KEY
    r = requests.get(UW_API_BASE + endpoint + ".json", params=params)
    assert r.status_code == 200
    value = r.json()
    return value["data"]