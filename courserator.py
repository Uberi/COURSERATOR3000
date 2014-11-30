#!/usr/bin/env python3

from datetime import datetime
import shelve

import course_info, solver

from flask import Flask, jsonify, request, url_for
from werkzeug.routing import BaseConverter, ValidationError

# set up application
app = Flask(__name__)

terms = {
    "2014S": (1145, datetime(2014, 5, 5), datetime(2014, 8, 16)),
    "2014F": (1149, datetime(2014, 5, 5), datetime(2014, 8, 16)),
    "2015W": (1151, datetime(2014, 9, 4), datetime(2015, 12, 19)),
    "2015S": (1155, datetime(2015, 1, 5), datetime(2015, 4, 25)),
    "2015F": (1159, datetime(2015, 5, 4), datetime(2015, 8, 15)),
}

class Schedule:
    def __init__(self, key, term, courses = set(), conflicts = set()):
        self.key = key
        self.term = term
        self.courses = courses
        self.conflicts = conflicts

class ScheduleConverter(BaseConverter):
    def to_python(self, value):
        if value not in datastore: raise ValidationError()
        return datastore[value]

    def to_url(self, schedule_value):
        return schedule_value.id
app.url_map.converters["schedule"] = ScheduleConverter

class ListConverter(BaseConverter):
    def to_python(self, value):
        return value.split("+")

    def to_url(self, values):
        return "+".join(BaseConverter.to_url(value) for value in values)
app.url_map.converters["list"] = ListConverter

@app.route("/")
def index():
    return "Stuff."

@app.route("/schedules", methods=["POST"])
def new_schedule():
    import uuid

    value = request.get_json(force=True)
    assert value["term"] in terms # validate term
    term = terms[value["term"]]

    key = str(uuid.uuid4()) # create a unique key
    datastore[key] = Schedule(key, term)
    return jsonify(id=key, url="/schedules/" + key)

@app.route("/schedules/<schedule:schedule>/term")
def get_term(schedule): return jsonify(term=next(x for x, term in terms if term == schedule.term))
@app.route("/schedules/<schedule:schedule>/term", methods=["PUT"])
def update_term(schedule):
    value = request.get_json(force=True)
    assert value["term"] in terms # validate term
    schedule.term = terms[value["term"]]
    datastore[schedule.key] = schedule; datastore.sync() # update schedule in datastore
    return jsonify(term=value["term"]) # return the new courses

@app.route("/schedules/<schedule:schedule>/courses")
def get_courses(schedule): return jsonify(courses=list(schedule.courses))
@app.route("/schedules/<schedule:schedule>/courses", methods=["PUT"])
def add_courses(schedule):
    courses = request.get_json(force=True)
    assert isinstance(courses, list)
    for course in courses: assert isinstance(course, str) # validate courses
    schedule.courses = set(courses)
    datastore[schedule.key] = schedule; datastore.sync() # update schedule in datastore
    return jsonify(courses=list(schedule.courses)) # return the new courses
@app.route("/schedules/<schedule:schedule>/courses/<list:courses>", methods=["DELETE"])
def remove_courses(schedule, courses):
    for course in courses:
        assert isinstance(course, str)
        schedule.courses.discard(course)
    datastore[schedule.key] = schedule; datastore.sync() # update schedule in datastore

@app.route("/schedules/<schedule:schedule>")
def get_schedules(schedule):
    courses_data = course_info.get_courses_data(schedule.term[0], schedule.courses)
    #from test_data import courses_data
    course_sections = course_info.get_courses_sections(courses_data, schedule.term[1], schedule.term[2])

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
            "instructors": list(instructors),
            "currently_enrolled": section_entry["enrollment_total"],
            "max_enrolled": section_entry["enrollment_capacity"],
            "title": section_entry["title"],
            "campus": section_entry["campus"],
            "note": section_entry["note"],
            "class_number": section_entry["class_number"],
        }

    json_schedules = [[section[0] + "|" + section[1] for section in schedule] for schedule in schedules]
    return jsonify(sections=json_sections_info, schedules=json_schedules)

if __name__ == "__main__":
    with shelve.open("schedules") as datastore:
        app.run(debug=True, port=5000) # debug mode
        #app.run(debug=False, host="0.0.0.0", port=80) # release mode - publicly visible