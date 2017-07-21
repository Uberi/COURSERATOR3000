#!/usr/bin/env python3

import itertools

import pycosat

class Scheduler:
    def __init__(self):
        self.constraints = []
        self.variable_index = 1 # used to generate unique variable names
        self.name_mapping = {}
        self.index_mapping = {}

    def constrain_requirement(self, variable_list):
        """
        Adds a course requirement constraint to the schedule.

        Generates CNF constraints such that exactly one of the variables in `variable_list` is true.
        """
        self.constraints.append(variable_list) # at least one variable is true
        self.constrain_conflict(variable_list) # every option of the same course conflicts with every other, to disallow taking the same course twice

    def constrain_conflict(self, variable_list):
        """
        Adds a schedule conflict constraint between specified mutually conflicting sections to the schedule.

        Generates CNF constraints such that zero or one of the variables in `variable_list` is true.
        """
        self.constraints += ([-a, -b] for a, b in itertools.combinations(variable_list, 2)) # no more than one variable is true

    def solve(self):
        """
        Produces an iterator for schedule possibilities that have no conflicts.

        Solves the constraints using a SAT solving algorithm and processes the results.
        """
        return ([self.index_mapping[y] for y in x if y > 0] for x in pycosat.itersolve(self.constraints))

    def register_variable(self, name):
        if name in self.name_mapping: return self.name_mapping[name]
        self.name_mapping[name] = self.variable_index
        self.index_mapping[self.variable_index] = name
        result = self.variable_index
        self.variable_index += 1
        return result

    def add_requirement(self, name, sections):
        section_variables = [self.register_variable((name, section)) for section in sections]
        self.constrain_requirement(section_variables)

    def add_conflict(self, section1, section2):
        conflict_variables = [self.register_variable(section1), self.register_variable(section2)]
        self.constrain_conflict(conflict_variables)

def block_compare(block1, block2):
    """
    Produces 0 if the blocks conflict, -1 if `block1` precedes `block2`, and 1 if `block1` follows `block2`.

    Blocks are 2-tuples where the first element is the start time of a section block as a `datetime`, and the second element is the block duration as a `timedelta`.
    """
    if block1[1] <= block2[0]: return -1 # `block1` is too early to conflict with `block2`
    if block1[0] >= block2[1]: return 1 # `block1` is too late to conflict with `block2`
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

def get_conflicts(requirements, course_sections): # O(pretty bad, but still polynomial at least)
    for (name1, requirements1), (name2, requirements2) in itertools.combinations(requirements.items(), 2):
        for section_name1 in requirements1:
            section_blocks1 = course_sections[(name1[0], section_name1)]
            for section_name2 in requirements2:
                section_blocks2 = course_sections[(name2[0], section_name2)]
                if check_section_conflict(section_blocks1, section_blocks2):
                    yield (name1[0], section_name1), (name2[0], section_name2)

def get_requirements(course_sections): # group sections by course and instruction type
    from collections import defaultdict
    requirements = defaultdict(list)
    for course, section in course_sections.keys():
        category = (course, section[:3]) # course code and instruction type (first three letters of section)
        requirements[category].append(section)
    return requirements

def compute_schedules(course_sections):
    """
    Computes a list of valid schedules given a course sections map.

    A course sections map is a dictionary mapping sections to lists of blocks.

    A section is a 2-tuple containing the course name and section name, both strings.

    A block is a 2-tuple containing the start and end dates/times, both `datetime.datetime` objects. This represents a specific meeting event.
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
    conflicts = list(get_conflicts(requirements, course_sections))
    for section1, section2 in conflicts:
        scheduler.add_conflict(section1, section2)
    print("\n".join(sorted(section1[0] + " " + section1[1] + "\tconflicts with\t" + section2[0] + " " + section2[1] for section1, section2 in conflicts)))

    print("=========================================================")
    print("=== solving for schedules")
    print("=========================================================")

    schedules = []
    limit = 500 # wip: boost this maybe
    for index, schedule in enumerate(scheduler.solve()):
        if index == limit: break
        schedules.append(schedule)

    possibility_space = 1
    for sections in requirements.values(): possibility_space *= len(sections)
    print(len(schedules), "valid schedules found out of", possibility_space, "possibilities")

    return schedules

if __name__ == "__main__":
    # test the scheduler
    s = Scheduler()
    s.add_requirement("CS246", ["LEC 001", "LEC 002", "LEC 003"])
    s.add_requirement("CS246", ["TUT 001", "TUT 002", "TUT 003"])
    s.add_requirement("CS245", ["LEC 001", "LEC 002", "LEC 003"])
    s.add_requirement("CS245", ["TUT 001", "TUT 002", "TUT 003"])
    s.add_conflict(("CS245", "LEC 001"), ("CS246", "LEC 003"))
    print("Non-conflicting schedules:")
    for schedule in s.solve():
        print(schedule)

    # test the conflict checker
    import datetime
    requirements = {
        ('CS240', 'LEC'): ['LEC 002', 'LEC 003', 'LEC 001'],
        ('ECON201', 'LEC'): ['LEC 002', 'LEC 003', 'LEC 001'],
        ('CS240', 'TUT'): ['TUT 104', 'TUT 101', 'TUT 103', 'TUT 102', 'TUT 105'],
        ('CS240', 'TST'): ['TST 201']
    }
    course_sections = {
        ('CS240', 'TUT 102'): [(datetime.datetime(2015, 1, 5, 14, 30), datetime.datetime(2015, 1, 5, 15, 20))],
        ('CS240', 'LEC 003'): [(datetime.datetime(2015, 1, 6, 11, 30), datetime.datetime(2015, 1, 6, 12, 50)),(datetime.datetime(2015, 1, 8, 11, 30), datetime.datetime(2015, 1, 8, 12, 50))],
        ('ECON201', 'LEC 003'): [(datetime.datetime(2015, 1, 6, 14, 30), datetime.datetime(2015, 1, 6, 15, 50)), (datetime.datetime(2015, 1, 8, 14, 30), datetime.datetime(2015, 1, 8, 15, 50))],
        ('CS240', 'TST 201'): [(datetime.datetime(2015, 2, 26, 16, 30), datetime.datetime(2015, 2, 26, 18, 20))],
        ('CS240', 'TUT 104'): [(datetime.datetime(2015, 1, 5, 16, 30), datetime.datetime(2015, 1, 5, 17, 20))],
        ('CS240', 'LEC 001'): [(datetime.datetime(2015, 1, 6, 13, 0), datetime.datetime(2015, 1, 6, 14, 20)), (datetime.datetime(2015, 1, 8, 13, 0), datetime.datetime(2015, 1, 8, 14, 20))],
        ('CS240', 'TUT 105'): [(datetime.datetime(2015, 1, 5, 15, 30), datetime.datetime(2015, 1, 5, 16, 20))],
        ('ECON201', 'LEC 002'): [(datetime.datetime(2015, 1, 5, 11, 30), datetime.datetime(2015, 1, 5, 12, 50)), (datetime.datetime(2015, 1, 7, 11, 30), datetime.datetime(2015, 1, 7, 12, 50))],
        ('CS240', 'LEC 002'): [(datetime.datetime(2015, 1, 6, 11, 30), datetime.datetime(2015, 1, 6, 12, 50)), (datetime.datetime(2015, 1, 8, 11, 30), datetime.datetime(2015, 1, 8, 12, 50))],
        ('CS240', 'TUT 101'): [(datetime.datetime(2015, 1, 5, 13, 30), datetime.datetime(2015, 1, 5, 14, 20))],
        ('CS240', 'TUT 103'): [(datetime.datetime(2015, 1, 5, 15, 30), datetime.datetime(2015, 1, 5, 16, 20))],
        ('ECON201', 'LEC 001'): [(datetime.datetime(2015, 1, 6, 13, 0), datetime.datetime(2015, 1, 6, 14, 20)), (datetime.datetime(2015, 1, 8, 13, 0), datetime.datetime(2015, 1, 8, 14, 20))]
    }
    print("Conflicts:")
    print(list(get_conflicts(requirements, course_sections)))