#!/usr/bin/env python3

import re
from datetime import datetime, timedelta

try:
    from .uwapi import uwapi # relative import
except SystemError: # not being used as a module
    from uwapi import uwapi # normal import

def parse_date(date_string, default_date):
    """Given a string `date_string` of the form MM/DD or YY/MM/DD or YYYY-MM-DD, returns the date it represents."""
    components = [int(digits) for digits in re.findall("\d+", date_string)]
    if len(components) == 2:
        return datetime(default_date.year, components[0], components[1]) # MM/DD date string
    if len(components) == 3:
        return datetime(components[0], components[1], components[2]) # YY/MM/DD date string
    return default_date

def get_term_names(max_term_count = 5):
    """Returns the `max_term_count` most recent term entries, and the term to select."""
    response = uwapi("terms/list")
    entries = sorted(
        (str(entry["id"]), entry["name"])
        for year, year_entries in response["listings"].items()
        for entry in year_entries
    )
    return str(response["next_term"]), entries[-max_term_count:]

def get_term_start_end_dates(term):
    """Returns the dates that lectures start and end for the given term code `term`."""
    response = uwapi("terms/{term}/importantdates".format(term=term))

    # compute default dates to use in case we can't find the lecture start/end dates for the term
    match = re.match("^(\d)(\d\d)(\d)$", term)
    assert match is not None
    start_date = datetime(1900 + int(match.group(1)) * 100 + int(match.group(2)), int(match.group(3)), 1)
    end_date = datetime(start_date.year + (start_date.month + 4) // 12, (start_date.month + 4) % 12, 1)

    # look for lecture start/end dates
    for important_date in response:
        if re.search(r"\bclasses\b.*\bbegin\b.*\buwaterloo\b", important_date["title"], re.IGNORECASE):
            start_date = parse_date(important_date["start_date"], start_date)
        elif re.search(r"\bclasses\b.*\bend\b", important_date["title"], re.IGNORECASE):
            end_date = parse_date(important_date["start_date"], start_date)
    
    return start_date, end_date

def get_courses_data(term, course_list):
    assert isinstance(term, str)
    result = {}
    for course in course_list:
        assert isinstance(course, str)
        subject, catalog_number = re.match("^\s*([a-zA-Z]+)\s*(\d\w*)\s*$", course).groups()
        assert subject and catalog_number
        result[course] = uwapi("terms/{term}/{subject}/{catalog_number}/schedule".format(term=term, subject=subject, catalog_number=catalog_number))
    return result

def get_class_times(description, default_start_date, default_end_date):
    #wip: do something with "is_closed" and "enrollment_capacity" and "enrollment_total", like an option to use even closed classes
    start_time_string, end_time_string, weekdays = description["start_time"], description["end_time"], description["weekdays"]
    if start_time_string is None or end_time_string is None or weekdays is None:
        return []
    start_date_string, end_date_string = description["start_date"], description["end_date"]

    # parse class imes like "14:05" into offsets from the beginning of the day
    hours, minutes = start_time_string.split(":")
    daily_start_offset = timedelta(minutes=int(minutes), hours=int(hours))
    hours, minutes = end_time_string.split(":")
    daily_end_offset = timedelta(minutes=int(minutes), hours=int(hours))

    # parse weekdays like "TThF" into a list of 2-tuples containing the offset of the beginning/end of each class for a given week
    weekday_offsets = {"M": 0, "T": 1, "W": 2, "Th": 3, "F": 4, "S": 5, "Su": 6}
    weekly_class_offsets = []
    for day in re.findall(r"Th|Su|M|T|W|F|S", weekdays):
        current_day = timedelta(days=weekday_offsets[day])
        weekly_class_offsets.append((current_day + daily_start_offset, current_day + daily_end_offset))

    # parse start/end dates
    if start_date_string is not None:
        start_date = parse_date(start_date_string, default_start_date)
    else:
        start_date = default_start_date
    if end_date_string is not None:
        end_date = parse_date(end_date_string, default_end_date) + timedelta(days=1) # add one day to include the ending date
    else:
        end_date = default_end_date + timedelta(days=1) # add one day to include the ending date

    # generate class list using the date range, days of week, and times of day
    all_class_times = []
    current_week_start = start_date - timedelta(days=start_date.weekday())  # beginning of the week containing the start date
    while current_week_start < end_date:
        for class_start_offset, class_end_offset in weekly_class_offsets:
            class_start = current_week_start + class_start_offset
            class_end = current_week_start + class_end_offset
            if class_start >= start_date and class_end <= end_date:
                all_class_times.append((class_start, class_end))

        current_week_start += timedelta(weeks=1)  # move to the next week

    return all_class_times

def get_courses_sections(courses_data, default_start_date, default_end_date):
    result = {}
    for course_name, course_data in courses_data.items():
        for section in course_data:
            times = []
            for classes in section["classes"]:
                times += get_class_times(classes["date"], default_start_date, default_end_date)
            result[(course_name, section["section"])] = sorted(times, key=lambda x: x[0])
    return result

def get_section_entries(courses_data, section_list):
    result = {}
    for course_name, section_name in section_list:
        for section in courses_data[course_name]:
            if section["section"] == section_name:
                result[(course_name, section_name)] = section
    return result

if __name__ == "__main__":
    courses_data = get_courses_data(1151, ["CS240"])
    print(get_courses_sections(courses_data, datetime(2015, 1, 5), datetime(2015, 5, 1)))
