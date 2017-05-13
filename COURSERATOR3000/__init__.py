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
        "2016W": (1161, datetime(2016, 1, 4), datetime(2016, 4, 23)),
        "2016S": (1165, datetime(2016, 5, 2), datetime(2016, 8, 13)),
        "2016F": (1169, datetime(2016, 9, 6), datetime(2016, 12, 22)),
        "2017W": (1171, datetime(2017, 1, 3), datetime(2017, 4, 25)),
        "2017S": (1175, datetime(2017, 5, 1), datetime(2017, 8, 11)),
        "2017F": (1179, datetime(2017, 9, 6), datetime(2016, 12, 22)),
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
        result = [course.strip() for course in value.split(",")]
        for course in result:
            if not re.match("^([a-zA-Z]+)\s*(\d\w*)$", course): raise ValidationError()
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
    if len(courses) > 10:
        return jsonify(
            sections={},
            schedules=[],
            schedule_stats=[],
        )
    
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
