#!/usr/bin/env python3

from collections import defaultdict
from datetime import datetime
import itertools

term = 1151 # winter 2015
term_start, term_end = datetime(2015, 1, 5), datetime(2015, 5, 1)
courses = ["CS246", "CS136"]

import course_info
from schedule import Schedule

def block_compare(block1, block2):
    """
    Produces 0 if the blocks conflict, -1 if `block1` precedes `block2`, and 1 if `block1` follows `block2`.
    """
    if block1[0] + block1[1] <= block2[0]: return -1 # `block1` is too early to conflict with `block2`
    if block1[0] >= block2[0] + block2[1]: return 1 # `block1` is too late to conflict with `block2`
    return 0 # blocks conflict with each other

def check_section_conflict(section1, section2):
    """
    Produces True if the sections conflict, and False otherwise.
    """
    index1, index2 = 0, 0
    while index1 < len(section1) and index2 < len(section2):
        status = block_compare(section1[index1], section1[index2])
        if status == -1: index1 += 1
        elif status == 1: index2 += 1
        else: return True # found conflicting block
    return False

# obtain a dictionary mapping course names to dictionaries mapping section names to lists of time blocks
course_sections = {course: course_info.get_course_sections(term, course, term_start, term_end) for course in courses}

# group sections by course and instruction type
requirements = defaultdict(list)
for course, sections in course_sections.items():
    for section, blocks in sections.items():
        category = (course, section[:3]) # course code and instruction type (first three letters of section)
        requirements[category].append(section)

# find section conflicts
conflicts = []
print([x for x in course_sections.values()])
for section1, section2 in itertools.product():
    print(section1, section2)
raise

s = Schedule()

# add requirements
for category, sections in requirements.items():
    s.add_requirement(category[0], sections)

#wip: find conflicts

#s.add_conflict(("CS245", "LEC 001"), ("CS246", "LEC 003"))

schedules = list(s.solve())
print(len(schedules))
