#!/usr/bin/env python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/COURSERATOR3000/")

from COURSERATOR3000 import app as application
application.secret_key = "COURSERATOR DOESN'T USE COOKIES, BUT IF IT DID WE WOULD PUT A SIGNING KEY HERE"
