#!/usr/bin/env python3

from collections import defaultdict
from datetime import datetime
import itertools

term = 1151 # winter 2015
term_start, term_end = datetime(2015, 1, 5), datetime(2015, 5, 1)
term_start, term_end = datetime(2015, 1, 5), datetime(2015, 1, 9)
courses = ["CS246", "CS136"]

import course_info
from scheduler import Scheduler

def block_compare(block1, block2):
    """
    Produces 0 if the blocks conflict, -1 if `block1` precedes `block2`, and 1 if `block1` follows `block2`.
    """
    if block1[0] + block1[1] <= block2[0]: return -1 # `block1` is too early to conflict with `block2`
    if block1[0] >= block2[0] + block2[1]: return 1 # `block1` is too late to conflict with `block2`
    return 0 # blocks conflict with each other

def check_section_conflict(section1, section2): # $O(n)$ where $n$ is `max(len(section1), len(section2))`
    """
    Produces True if the sections conflict, and False otherwise.
    """
    index1, index2 = 0, 0
    while index1 < len(section1) and index2 < len(section2):
        status = block_compare(section1[index1], section1[index2])
        if status == -1: index1 += 1
        elif status == 1: index2 += 1
        else: # found conflicting block
            return True
    return False

def get_requirements(course_sections): # group sections by course and instruction type
    requirements = defaultdict(list)
    for course, sections in course_sections.items():
        for section, blocks in sections.items():
            category = (course, section[:3]) # course code and instruction type (first three letters of section)
            requirements[category].append(section)
    return requirements

def get_conflicts(requirements, course_sections):
    for (name1, requirements1), (name2, requirements2) in itertools.combinations(requirements.items(), 2):
        for section_name1 in requirements1:
            section_blocks1 = course_sections[name1[0]][section_name1]
            for section_name2 in requirements2:
                section_blocks2 = course_sections[name2[0]][section_name2]
                if check_section_conflict(section_blocks1, section_blocks2):
                    yield (name1[0], section_name1), (name2[0], section_name2)

# obtain a dictionary mapping course names to dictionaries mapping section names to lists of time blocks
course_sections = {course: course_info.get_course_sections(term, course, term_start, term_end) for course in courses}

scheduler = Scheduler()

print("=== generating requirement constraints")

# group sections by course and instruction type
requirements = get_requirements(course_sections)
for requirement, sections in requirements.items():
    scheduler.add_requirement(requirement[0], sections)
    print(requirement[0] + " " + requirement[1] + "\t" + ", ".join(sections))

print("=== generating conflict constraints")

# find section conflicts
conflicts = list(get_conflicts(requirements, course_sections))[:1]
for section1, section2 in conflicts:
    scheduler.add_conflict(section1, section2)
print("\n".join(sorted(section1[0] + " " + section1[1] + " conflicts with " + section2[0] + " " + section2[1] for section1, section2 in conflicts)))

print(scheduler.constraints)

schedules = list(scheduler.solve())

print("=== solved for schedules")

possibility_space = 1
for sections in requirements.values():
    possibility_space *= len(sections)

print("schedule candidates:", possibility_space)
print("number of schedules:", len(schedules))
for schedule in schedules:
    print(schedule)
