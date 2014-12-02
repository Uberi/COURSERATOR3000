#!/usr/bin/env python3

from datetime import datetime
import shelve

import course_info, solver

from flask import Flask, jsonify, request
from werkzeug.routing import BaseConverter, ValidationError

# set up application
app = Flask(__name__)

class TermConverter(BaseConverter):
    terms = {
        "2014S": (1145, datetime(2014, 5, 5), datetime(2014, 8, 16)),
        "2014F": (1149, datetime(2014, 9, 4), datetime(2014, 12, 19)),
        "2015W": (1151, datetime(2015, 1, 5), datetime(2015, 4, 25)),
        "2015S": (1155, datetime(2015, 5, 4), datetime(2015, 8, 15)),
    }
    
    def to_python(self, value):
        if value not in self.terms: raise ValidationError()
        return self.terms[value]

    def to_url(self, term_value):
        return next(k for k, v in self.terms if v == term_value)
app.url_map.converters["term"] = TermConverter

class CourseListConverter(BaseConverter):
    def to_python(self, value):
        import re
        result = value.split(",")
        for course in result:
            if not re.match("^\s*([a-zA-Z]+)\s*(\d\w*)\s*$", course): raise ValidationError()
        return result

    def to_url(self, values):
        return ",".join(BaseConverter.to_url(value) for value in values)
app.url_map.converters["courselist"] = CourseListConverter

@app.route("/")
def index():
    return "Stuff."

@app.route("/schedules/<term:term>/<courselist:courses>")
def get_schedules(term, courses):
    courses_data = course_info.get_courses_data(term[0], courses)
    #from test_data import courses_data
    
    course_sections = course_info.get_courses_sections(courses_data, term[1], term[2])

    schedules = solver.compute_schedules(course_sections)

    sections = {section for schedule in schedules for section in schedule} # set of every section in every schedules
    section_entries = course_info.get_section_entries(courses_data, sections)
    json_sections_info = {}
    for section, section_entry in section_entries.items():
        instructors = set()
        #wip: keep track of locations
        for class_entry in section_entry["classes"]:
            instructors.update(class_entry["instructors"])
        json_sections_info[section[0] + "|" + section[1]] = {
            "name": section_entry["subject"] + section_entry["catalog_number"],
            "section": section_entry["section"],
            "instructors": list(instructors),
            "currently_enrolled": section_entry["enrollment_total"],
            "max_enrolled": section_entry["enrollment_capacity"],
            "title": section_entry["title"],
            "campus": section_entry["campus"],
            "note": section_entry["note"],
            "class_number": section_entry["class_number"],
            "blocks": course_sections[section],
        }

    json_schedules = [[section[0] + "|" + section[1] for section in schedule] for schedule in schedules]
    return jsonify(sections=json_sections_info, schedules=json_schedules)

if __name__ == "__main__":
    with shelve.open("schedules") as datastore:
        app.run(debug=True, port=5000) # debug mode
        #app.run(debug=False, host="0.0.0.0", port=80) # release mode - publicly visible