#!/usr/bin/env python3

import re
from datetime import timedelta, datetime

def get_class_times(description, default_start_date, default_end_date):
    # parse daily times
    hours, minutes = map(int, description["start_time"].split(":"))
    daily_start = timedelta(0, 0, 0, 0, minutes, hours)
    hours, minutes = map(int, description["end_time"].split(":"))
    daily_end = timedelta(0, 0, 0, 0, minutes, hours)
    
    # parse weekdays
    weekdays = {"M": 0, "T": 1, "W": 2, "Th": 3, "F": 4, "S": 5, "Su": 6}
    weekday_pattern = re.compile(r"M|T|W|Th|F|S|Su")
    weekly_classes = []
    for day in re.findall(weekday_pattern, description["weekdays"]):
        current_day = timedelta(weekdays[day])
        weekly_classes.append((current_day + daily_start, daily_end - daily_start))
    
    # parse start/end dates
    start = default_start_date
    if description["start_date"] != None:
        years, months, days = description["start_date"].split("-")
        start = datetime(years, months, days)
    end = default_end_date
    if description["start_date"] != None:
        years, months, days = description["end_date"].split("-")
        end = datetime(years, months, days)
    
    # generate class list
    result = []
    current_date = start
    one_week = timedelta(0, 0, 0, 0, 0, 0, 1)
    while current_date < end + one_week: # loop for an extra week to make sure we get the last week correct
        for class_offset, duration in weekly_classes:
            class_start = current_date + class_offset
            if class_start + duration <= end:
                result.append((class_start, duration))
        current_date = current_date + one_week
    return result

description = {
    "start_time":"12:30",
    "end_time":"13:50",
    "weekdays":"MW",
    "start_date":None,
    "end_date":None,
    "is_tba":False,
    "is_cancelled":False,
    "is_closed":False
}

print([x for x in get_class_times(description, datetime(2014, 11, 24), datetime(2014, 11, 28))])
