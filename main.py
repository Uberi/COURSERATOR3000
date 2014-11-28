#!/usr/bin/env python3

import itertools

class Schedule:
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
        self.constraints += ([-x[0], -x[1]] for x in itertools.combinations(variable_list, 2)) # no more than one variable is true

    def solve(self):
        """
        Produces an iterator for schedule possibilities that have no conflicts.
        
        Solves the constraints using a SAT solving algorithm and processes the results.
        """
        import pycosat
        return ({self.index_mapping[y] for y in x if y > 0} for x in pycosat.itersolve(s.constraints))
    
    def register_variable(self, name):
        if name in self.name_mapping: return self.name_mapping[name]
        self.name_mapping[name] = self.variable_index
        self.index_mapping[self.variable_index] = name
        result = self.variable_index
        self.variable_index += 1
        return result
    
    def add_course(self, name, lecture_sections = None, tutorial_sections = None, lab_sections = None):
        if lecture_sections != None:
            sections = [self.register_variable((name, section)) for section in lecture_sections]
            self.constrain_requirement(sections)
        if tutorial_sections != None:
            sections = [self.register_variable((name, section)) for section in tutorial_sections]
            self.constrain_requirement(sections)
        if lab_sections != None:
            sections = [self.register_variable((name, section)) for section in lab_sections]
            self.constrain_requirement(sections)
    
    def add_conflict(self, section1, section2):
        self.constrain_conflict([self.register_variable(section1), self.register_variable(section2)])

s = Schedule()
s.add_course("CS246", ["LEC1", "LEC2", "LEC3"], ["TUT1", "TUT2", "TUT3"])
s.add_course("CS245", ["LEC1", "LEC2", "LEC3"], ["TUT1", "TUT2", "TUT3"])
s.add_conflict(("CS245", "LEC1"), ("CS246", "LEC3"))
for schedule in s.solve():
    print(schedule)
