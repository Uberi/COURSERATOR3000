#!/usr/bin/env python3

from datetime import datetime, time

from flask import Flask, jsonify, request
from werkzeug.routing import BaseConverter, ValidationError

try:
    from . import course_info, scheduler # relative import
except SystemError: # not being used as a module
    import course_info, scheduler # normal import

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

@app.route('/lib/<path:path>')
def static_lib_proxy(path): return app.send_static_file("lib/" + path) # MIME type is guessed automatically

@app.route("/")
def index(): return app.send_static_file("index.html") # MIME type is guessed automatically

@app.route("/schedules/<term:term>/<courselist:courses>")
def get_schedules(term, courses):
    courses_data = course_info.get_courses_data(term[0], courses)
    #from test_data import courses_data
    
    course_sections = course_info.get_courses_sections(courses_data, term[1], term[2])
    schedules = scheduler.compute_schedules(course_sections)

    sections = {section for schedule in schedules for section in schedule} # set of every section in every schedules
    section_entries = course_info.get_section_entries(courses_data, sections)

    # compute section info
    json_sections_info = {}
    for section, section_entry in section_entries.items():
        instructors = set()
        #wip: keep track of locations
        for class_entry in section_entry["classes"]:
            instructors.update(class_entry["instructors"])
        try:
            earliest = min(start.time() for start, end in course_sections[section]).strftime("%H:%M")
            latest = max(end.time() for start, end in course_sections[section]).strftime("%H:%M")
        except ValueError:
            earliest, latest = None, None
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
            "blocks": [(start.isoformat(), end.isoformat()) for start, end in course_sections[section]],
            "earliest": earliest,
            "latest": latest,
        }

    # compute schedule info
    json_schedules = [[section[0] + "|" + section[1] for section in schedule] for schedule in schedules]

    #compute schedule stats
    json_stats = []
    for schedule in json_schedules:
        earliest, latest = "9", "/" # beyond the max and min values
        instructors = set()
        for section_identifier in schedule:
            section = json_sections_info[section_identifier]
            instructors.update(section["instructors"])
            if section["earliest"] is not None and section["earliest"] < earliest:
                earliest = section["earliest"]
            if section["latest"] is not None and section["latest"] > latest:
                latest = section["latest"]
        json_stats.append({
            "earliest": earliest if earliest != "9" else "-",
            "latest": latest if latest != "/" else "-",
            "instructors": sorted(instructors),
        })

    return jsonify(
        sections=json_sections_info,
        schedules=json_schedules,
        schedule_stats=json_stats,
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000) # debug mode
    #app.run(debug=False, host="0.0.0.0", port=80) # release mode - publicly visible
