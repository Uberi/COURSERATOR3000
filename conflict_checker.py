#!/usr/bin/env python3

import itertools

def block_compare(block1, block2):
    """
    Produces 0 if the blocks conflict, -1 if `block1` precedes `block2`, and 1 if `block1` follows `block2`.
    
    Blocks are 2-tuples where the first element is the start time of a section block as a `datetime`, and the second element is the block duration as a `timedelta`.
    """
    if block1[0] + block1[1] <= block2[0]: return -1 # `block1` is too early to conflict with `block2`
    if block1[0] >= block2[0] + block2[1]: return 1 # `block1` is too late to conflict with `block2`
    return 0 # blocks conflict with each other

def check_section_conflict(section1, section2): # $O(n)$ where $n$ is `max(len(section1), len(section2))`
    """
    Produces True if `section1` conflicts with `section2`, and False otherwise.
    
    Sections are lists of blocks.
    """
    index1, index2 = 0, 0
    while index1 < len(section1) and index2 < len(section2):
        status = block_compare(section1[index1], section2[index2])
        if status == -1: index1 += 1
        elif status == 1: index2 += 1
        else: # found conflicting block
            return True
    return False

def get_conflicts(requirements, course_sections):
    for (name1, requirements1), (name2, requirements2) in itertools.combinations(requirements.items(), 2):
        for section_name1 in requirements1:
            section_blocks1 = course_sections[(name1[0], section_name1)]
            for section_name2 in requirements2:
                section_blocks2 = course_sections[(name2[0], section_name2)]
                if check_section_conflict(section_blocks1, section_blocks2):
                    yield (name1[0], section_name1), (name2[0], section_name2)

if __name__ == "__main__":
    import datetime
    requirements = {
        ('CS240', 'LEC'): ['LEC 002', 'LEC 003', 'LEC 001'],
        ('ECON201', 'LEC'): ['LEC 002', 'LEC 003', 'LEC 001'],
        ('CS240', 'TUT'): ['TUT 104', 'TUT 101', 'TUT 103', 'TUT 102', 'TUT 105'],
        ('CS240', 'TST'): ['TST 201']
    }
    course_sections = {
        ('CS240', 'TST 201'): [(datetime.datetime(2015, 2, 26, 16, 30), datetime.timedelta(0, 6600))],
        ('CS240', 'TUT 102'): [(datetime.datetime(2015, 1, 5, 14, 30), datetime.timedelta(0, 3000))],
        ('CS240', 'TUT 104'): [(datetime.datetime(2015, 1, 5, 16, 30), datetime.timedelta(0, 3000))],
        ('CS240', 'TUT 105'): [(datetime.datetime(2015, 1, 5, 15, 30), datetime.timedelta(0, 3000))],
        ('CS240', 'LEC 002'): [(datetime.datetime(2015, 1, 6, 11, 30), datetime.timedelta(0, 4800)), (datetime.datetime(2015, 1, 8, 11, 30), datetime.timedelta(0, 4800))],
        ('CS240', 'LEC 001'): [(datetime.datetime(2015, 1, 6, 13, 0), datetime.timedelta(0, 4800)), (datetime.datetime(2015, 1, 8, 13, 0), datetime.timedelta(0, 4800))],
        ('CS240', 'LEC 003'): [(datetime.datetime(2015, 1, 6, 11, 30), datetime.timedelta(0, 4800)), (datetime.datetime(2015, 1, 8, 11, 30), datetime.timedelta(0, 4800))],
        ('CS240', 'TUT 101'): [(datetime.datetime(2015, 1, 5, 13, 30), datetime.timedelta(0, 3000))],
        ('CS240', 'TUT 103'): [(datetime.datetime(2015, 1, 5, 15, 30), datetime.timedelta(0, 3000))],
        ('ECON201', 'LEC 002'): [(datetime.datetime(2015, 1, 5, 11, 30), datetime.timedelta(0, 4800)), (datetime.datetime(2015, 1, 7, 11, 30), datetime.timedelta(0, 4800))],
        ('ECON201', 'LEC 001'): [(datetime.datetime(2015, 1, 6, 13, 0), datetime.timedelta(0, 4800)), (datetime.datetime(2015, 1, 8, 13, 0), datetime.timedelta(0, 4800))],
        ('ECON201', 'LEC 003'): [(datetime.datetime(2015, 1, 6, 14, 30), datetime.timedelta(0, 4800)), (datetime.datetime(2015, 1, 8, 14, 30), datetime.timedelta(0, 4800))],
    }
    print(list(get_conflicts(requirements, course_sections)))
