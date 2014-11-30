#!/usr/bin/env python3

from collections import defaultdict
from datetime import datetime, timedelta

from scheduler import Scheduler
import conflict_checker

def get_requirements(course_sections): # group sections by course and instruction type
    requirements = defaultdict(list)
    for (course, section), blocks in course_sections.items():
        category = (course, section[:3]) # course code and instruction type (first three letters of section)
        requirements[category].append(section)
    return requirements

def compute_schedules(course_sections):
    """
    Computes a list of valid schedules given a course sections map.

    A course sections map is a dictionary mapping course names to dictionaries mapping section names to a list of sections.

    A section is a 2-tuple containing the course name and section name, both strings.
    """
    scheduler = Scheduler()

    # group sections by course and instruction type
    requirements = get_requirements(course_sections)
    for requirement, sections in requirements.items():
        scheduler.add_requirement(requirement[0], sections)

    print("=========================================================")
    print("=== generating conflict constraints")
    print("=========================================================")

    # find section conflicts
    conflicts = list(conflict_checker.get_conflicts(requirements, course_sections))
    for section1, section2 in conflicts:
        scheduler.add_conflict(section1, section2)
    print("\n".join(sorted(section1[0] + " " + section1[1] + "\tconflicts with\t" + section2[0] + " " + section2[1] for section1, section2 in conflicts)))

    print("=========================================================")
    print("=== solving for schedules")
    print("=========================================================")

    schedules = list(scheduler.solve())

    possibility_space = 1
    for sections in requirements.values(): possibility_space *= len(sections)
    print(len(schedules), "valid schedules found out of", possibility_space, "possibilities")

    return schedules

def get_schedule_json(course_sections, schedule, start, end):
    """
    Given a schedule and time listings for various course sections, calculates every class in that schedule between `start` and `end`.

    A schedule is simply a list of sections.

    A section is a 2-tuple containing the course name and section name, both strings.
    """
    end = end + timedelta(days=1) # add one day to represent the end of that day
    result = []
    for section in schedule:
        for block in course_sections[section]:
            if start <= block[0] and block[0] + block[1] < end:
                result.append({
                    "start": (block[0] - start).total_seconds(),
                    "duration": block[1].total_seconds(),
                    "class": section[0],
                    "section": section[1],
                })
    result = sorted(result, key=lambda x: x["start"])
    return result