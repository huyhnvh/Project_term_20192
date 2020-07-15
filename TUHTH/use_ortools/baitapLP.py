from __future__ import print_function
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver("btlp", pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
c0 = solver.constraints()