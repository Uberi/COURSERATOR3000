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
        return ({self.index_mapping[y] for y in x if y > 0} for x in pycosat.itersolve(self.constraints))

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

if __name__ == "__main__":
    s = Scheduler()
    s.add_requirement("CS246", ["LEC 001", "LEC 002", "LEC 003"])
    s.add_requirement("CS246", ["TUT 001", "TUT 002", "TUT 003"])
    s.add_requirement("CS245", ["LEC 001", "LEC 002", "LEC 003"])
    s.add_requirement("CS245", ["TUT 001", "TUT 002", "TUT 003"])
    s.add_conflict(("CS245", "LEC 001"), ("CS246", "LEC 003"))
    print("Non-conflicting schedules:")
    for schedule in s.solve():
        print(schedule)