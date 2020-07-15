#!/usr/bin/python
# -*- coding: utf-8 -*-
import ortools
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
from collections import namedtuple
import numpy as np
import pulp
import math
from local_search import GuidedLocalSearch


Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

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

def CP_solver_ortools(facility_count, customer_count, facilities, customers):
    demand = [] #demand
    setup_cost = [] #setup cost
    for j in range(customer_count):
        demand.append(customers[j].demand)
    for i in range(facility_count):
        setup_cost.append(int(facilities[i].setup_cost))
    # dist
    d = [[0 for j in range(customer_count)]for i in range(facility_count)]
    for i in range(facility_count):
        for j in range(customer_count):
            d[i][j] = int(length(facilities[i].location, customers[j].location))
    # model
    model = cp_model.CpModel()
    x = [[model.NewIntVar(0,1, "x[%i][%i]" %(i, j)) for j in range(customer_count)] for i in range(facility_count)]
    y = [model.NewIntVar(0,1, str(i)) for i in range(facility_count)]
    # 1 customer by 1 facility
    for j in range(customer_count):
        model.Add(sum([x[i][j] for i in range(facility_count)]) == 1 )
    # capacity >= sum demand
    for i in range(facility_count):
        model.Add(cp_model._ScalProd(x[i], demand) <= facilities[i].capacity)
    # y[i] facility[i] used?
    for i in range(facility_count):
        for j in range(customer_count):
            model.Add(y[i] >= x[i][j])
    # sum dist cost list
    dc = [model.NewIntVar(0,1<<30, "dc[%i]" %(j)) for j in range(facility_count)]
    for i in range(facility_count):
        model.Add(dc[i] == cp_model._ScalProd(x[i],d[i]))
    model.Minimize(cp_model._ScalProd(y,setup_cost) + sum(dc))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5*60
    status = solver.Solve(model)
    solution = []
    obj = 0
    if(status == cp_model.FEASIBLE or status == cp_model.OPTIMAL):
        obj = solver.ObjectiveValue()
        for j in range(customer_count):
            for i in range(facility_count):
                if(solver.Value(x[i][j]) > 0):
                    solution.append(i)
                    break
    
    else :
        print("don't have solution!")
    return obj, solution

def linear_solver_pulp(facility_count, customer_count, facilities, customers):
    # dist
    dist = [[0 for j in range(customer_count)]for i in range(facility_count)]
    for i in range(facility_count):
        for j in range(customer_count):
            dist[i][j] = int(length(facilities[i].location, customers[j].location))
    model = pulp.LpProblem("model", pulp.LpMinimize)
    # add variables
    x = pulp.LpVariable.dicts('facility',((i,j) for i in range(facility_count) for j in range(customer_count)),cat = "Binary")
    y = pulp.LpVariable.dicts('customer',range(facility_count),cat = "Binary")
    # add objective function
    model += pulp.lpSum(y[i]*facilities[i].setup_cost for i in range(facility_count))\
            + pulp.lpSum(x[(i,j)]*dist[i][j] for i in range(facility_count) for j in range(customer_count))
    # add constraint
    for j in range(customer_count):
        model += pulp.lpSum(x[(i,j)] for i in range(facility_count)) == 1

    for i in range(facility_count):
        model += pulp.lpSum(x[(i,j)]*customers[j].demand for j in range(customer_count)) <= facilities[i].capacity

    for i in range(facility_count):
        for j in range(customer_count):
            model += y[i] >= x[(i,j)]
    model.solve()
    status = pulp.LpStatus[model.status]
    solution =[]
    obj = 0
    if(status == 'Optimal' or status == 'Feasible'):
        obj = pulp.value(model.objective)
        for j in range(customer_count):
            for i in range(facility_count):
                if(x[(i,j)].varValue > 0):
                    solution.append(i)
                    break
    
    return obj, solution

def greedy_solver(facility_count, customer_count, facilities, customers):
    solution = [0 for i in range(customer_count)]
    obj = 0
    dist = [[0 for j in range(customer_count)] for i in range(facility_count)]
    for i in range(facility_count):
        for j in range(customer_count):
            dist[i][j] = length(facilities[i].location , customers[j].location)
    capacities = [facilities[i].capacity for i in range(facility_count)]
    facility_used = [0 for i in range(facility_count)]
    for j in range(customer_count):
        min_cost = 1<<30
        f = 0
        for i in range(facility_count):
            cost = 0
            if(capacities[i] - customers[j].demand >= 0):
                cost += dist[i][j]
                # if(facility_used[i] == 0):
                cost += facilities[i].setup_cost 
                if(min_cost >  cost):
                    min_cost = cost
                    f = i
        solution[j] = f
        capacities[f] -= customers[j].demand 
        facility_used[f] = 1 
        # obj += min_cost
    for j in range(customer_count):
        obj += dist[solution[j]][j]
    for i in range(facility_count):
        obj += facility_used[i]*facilities[i].setup_cost
    return obj, solution 
     

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))
    facilities_list_change = [i for i in range(facility_count)]
    customers_list_change = [i for i in range(customer_count)]
    if facility_count*customer_count < 100000:
        obj, solution = MIP_solver_ortools(facilities_list_change, customers_list_change, facilities, customers)
        output_data = '%.2f' % obj + ' ' + str(0) + '\n'
        output_data += ' '.join(map(str, solution))
    else:
        f = open('guided_result_'+str(facility_count)+'_'+str(customer_count), 'r')
        output_data = f.read()
    
    # obj, solution = CP_solver_ortools(facility_count, customer_count,facilities, customers)
    # obj, solution = linear_solver_ortools(facility_count, customer_count,facilities, customers)
    # obj, solution = greedy_solver(facility_count, customer_count,facilities, customers)
    # local_search = GuidedLocalSearch()
    # obj, solution = local_search.search(facilities, customers)
    
    # prepare the solution in the specified output format
    # output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    # output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')

