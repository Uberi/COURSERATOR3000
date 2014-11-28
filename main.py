#!/usr/bin/env python3

#import course_info
from schedule import Schedule

s = Schedule()
s.add_requirement("CS246", ["LEC 001", "LEC 002", "LEC 003"])
s.add_requirement("CS246", ["TUT 001", "TUT 002", "TUT 003"])
s.add_requirement("CS245", ["LEC 001", "LEC 002", "LEC 003"])
s.add_requirement("CS245", ["TUT 001", "TUT 002", "TUT 003"])
s.add_conflict(("CS245", "LEC 001"), ("CS246", "LEC 003"))
for schedule in s.solve():
    print(schedule)
