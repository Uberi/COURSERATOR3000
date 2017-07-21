#!/usr/bin/env python3

import re
from datetime import datetime

from flask import Flask, jsonify, render_template
from werkzeug.routing import BaseConverter, ValidationError

try:  # when used as a module, do relative import
    from . import course_info
    from . import scheduler
except SystemError:  # not being used as a module, do normal import
    import course_info
    import scheduler

# set up application
app = Flask(__name__, static_url_path="/static")


class TermConverter(BaseConverter):
    def to_python(self, value):
        match = re.match("^\d{4}$", value)
        if not match:
            raise ValidationError()
        return value

    def to_url(self, term_code):
        return term_code
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


@app.route("/")
def index():
    term_to_select, terms = course_info.get_term_names()
    return render_template('index.html', term_to_select=term_to_select, terms=terms)


@app.route("/schedules/<term:term>/<courselist:courses>")
def get_schedules(term, courses):
    if len(courses) > 10:
        return jsonify(
            sections={},
            schedules=[],
            schedule_stats=[],
        )

    term_start, term_end = course_info.get_term_start_end_dates(term)
    courses_data = course_info.get_courses_data(term, courses)
    # from test_data import courses_data

    course_sections = course_info.get_courses_sections(courses_data, term_start, term_end)
    schedules = scheduler.compute_schedules(course_sections)

    sections = {section for schedule in schedules for section in schedule}  # set of every section in every schedule
    section_entries = course_info.get_section_entries(courses_data, sections)

    # compute section info
    json_sections_info = {}
    for section, section_entry in section_entries.items():
        instructors = set()
        # wip: keep track of locations
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

    # compute schedule stats
    json_stats = []
    for schedule in json_schedules:
        earliest, latest = None, None
        instructors = set()
        for section_identifier in schedule:
            section = json_sections_info[section_identifier]
            instructors.update(section["instructors"])
            if section["earliest"] is not None and (earliest is None or section["earliest"] < earliest):
                earliest = section["earliest"]
            if section["latest"] is not None and (latest is None or section["latest"] > latest):
                latest = section["latest"]
        json_stats.append({
            "earliest": "-" if earliest is None else earliest,
            "latest": "-" if latest is None else latest,
            "instructors": sorted(instructors),
        })

    return jsonify(
        sections=json_sections_info,
        schedules=json_schedules,
        schedule_stats=json_stats,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8888)  # debug mode
    # app.run(debug=False, host="0.0.0.0", port=80)  # release mode - publicly visible
