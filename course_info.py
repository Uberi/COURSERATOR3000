#!/usr/bin/env python3

import re
from datetime import timedelta, datetime

from uwapi import uwapi

def parse_date(value, default_date):
    components = list(map(int, re.findall("\d+", value)))
    assert 2 <= len(components) <= 3
    if len(components) == 2: # month and day specified
        return datetime(default_date.year, components[0], components[1])
    return datetime(components[0], components[1], components[2]) # year, month, and day specified

def get_class_times(description, default_start_date, default_end_date):
    if description["start_time"] == None or description["end_time"] == None: # no specified time
        return []
    
    # parse daily times
    hours, minutes = map(int, description["start_time"].split(":"))
    daily_start = timedelta(0, 0, 0, 0, minutes, hours)
    hours, minutes = map(int, description["end_time"].split(":"))
    daily_end = timedelta(0, 0, 0, 0, minutes, hours)
    
    # parse weekdays
    weekdays = {"M": 0, "T": 1, "W": 2, "Th": 3, "F": 4, "S": 5, "Su": 6}
    weekly_classes = []
    for day in re.findall(r"M|T|W|Th|F|S|Su", description["weekdays"]):
        current_day = timedelta(weekdays[day])
        weekly_classes.append((current_day + daily_start, daily_end - daily_start))
    
    # parse start/end dates
    start = parse_date(description["start_date"], default_start_date) if description["start_date"] != None else default_start_date
    end = parse_date(description["end_date"], default_end_date) if description["end_date"] != None else default_end_date
    end = end + timedelta(1) # add one day to compare against the end of the day
    
    # generate class list
    result = []
    current_date = start - timedelta(start.weekday()) # beginning of the week containing the start date
    one_week = timedelta(0, 0, 0, 0, 0, 0, 1)
    while current_date < end:
        for class_offset, duration in weekly_classes:
            class_start = current_date + class_offset
            if class_start >= start and class_start + duration < end:
                result.append((class_start, duration))
        current_date = current_date + one_week
    return result

def get_course_sections(term, course, default_start_date, default_end_date):
    subject, catalog_number = re.match("([a-zA-Z]+)\s*(\d+)", course).groups()
    course_data = uwapi("terms/{0}/{1}/{2}/schedule".format(term, subject, catalog_number))
    
    result = {}
    for section in course_data:
        times = []
        for classes in section["classes"]:
            times += get_class_times(classes["date"], default_start_date, default_end_date)
        result[section["section"]] = sorted(times, key=lambda x: x[0])
    return result