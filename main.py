#!/usr/bin/env python3

import itertools

class Schedule:
    def __init__(self):
        self.constraints = []
        self.variable_index = 1 # used to generate unique variable names
        self.variable_mapping = {}
    
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
        return ([y for y in x if y > 0] for x in pycosat.itersolve(s.constraints))
    
    def add_course(self, name, lecture_sections = None, tutorial_sections = None, lab_sections = None):
        if lecture_sections != None:
            pass

s = Schedule()
#s.add_course("CS246", ["LEC1", "LEC2", "LEC3"])
s.constrain_course([1, 2, 3])
s.constrain_course([4, 5, 6])
print(list(s.solve()))

import sys
sys.exit()
