import ortools
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
from collections import namedtuple
import numpy as np
import pulp
import math

def MIP_solver_ortools(facilities_list_change, customers_list_change, facilities, customers):
    facility_count = len(facilities_list_change)
    customer_count = len(customers_list_change)
    solver = pywraplp.Solver("solve_mip", pywraplp.Solver.CLP_LINEAR_PROGRAMMING)
    x = [[solver.IntVar(0,1,'[%i][%i]' %(i, j)) for j in range(customer_count)]for i in range(facility_count)]
    y = [solver.IntVar(0,1, "[%i]" %(i)) for i  in range(facility_count)]
    # infinity = solver.infinity()
    # Calculate length from facility to customer
    d = [[0 for j in range(customer_count)]for i in range(facility_count)]
    for i in range(facility_count):
        for j in range(customer_count):
            _i = facilities_list_change[i]
            _j = customers_list_change[j]
            d[i][j] = length(facilities[_i].location, customers[_j].location)
    # add constraint 1
    constraint1 = [solver.Constraint(1,1) for j in range(customer_count)]
    for j in range(customer_count):
        for i in range(facility_count):
            constraint1[j].SetCoefficient(x[i][j], 1)
    # add constraint 2
    constraint2 = [solver.Constraint(0, facilities[i].capacity) for i in facilities_list_change]
    for i in range(facility_count):
        for j in range(customer_count):
            _j = customers_list_change[j]
            constraint2[i].SetCoefficient(x[i][j], customers[_j].demand)
    # add constraint 3
    constraint3 = [[solver.Constraint(0,1) for j in range(customer_count)] for i in range(facility_count)]
    for i in range(facility_count):
        for j in range(customer_count):
            constraint3[i][j].SetCoefficient(y[i], 1)
            constraint3[i][j].SetCoefficient(x[i][j], -1)
    # add objective
    objt = solver.Objective()
    for i in range(facility_count):
        _i = facilities_list_change[i]
        objt.SetCoefficient(y[i], facilities[_i].setup_cost)
        for j in range(customer_count):
            objt.SetCoefficient(x[i][j], d[i][j])
    objt.SetMinimization()
    # solver.set_time_limit = 60000
    # solver.Minimize(sum(y[i]*facilities[i].setup_cost + sum(x[i][j]*d[i][j] for j in range(customer_count)) for i in range(facility_count)))
    # run MIP and return solution if have optimal solution
    status = solver.Solve()
    solution = np.array([0 for i in range(len(customers))])
    obj = 0
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        obj = solver.Objective().Value()
        for j in range(customer_count):
            _j = customers_list_change[j]
            for i in range(facility_count):
                if(x[i][j].solution_value() > 0):
                    solution[_j] = int(facilities_list_change[i])
                    break
    else :
        print("don't find solution!")
        return
    return obj, solution 


