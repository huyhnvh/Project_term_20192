#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
import math
import time
from local_search import TabuSearch

def vertex_coloring(E,NC,SC,list_id, near_list):
    l = []
    model = cp_model.CpModel()
    cVar =[model.NewIntVar(0, SC-1, str(i)) for i in range(NC)]
    for i in range(NC):
        k=i
        if(i>=SC):
            k=SC
        model.Add(cVar[list_id[i]] <= k)
    # for i in range(NC):
    #     for j in range(i+1,NC):
    #         if (near_list[list_id[i]][list_id[j]] == 1):
    #             model.Add(cVar[list_id[j]] != cVar[list_id[i]] )
        
    for p in E:
        model.Add(cVar[(p[0])] != cVar[(p[1])])
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status == cp_model.FEASIBLE:
        for i in range(NC):
            l.append(int(solver.Value(cVar[i])))
        return l
    else:
        return []

def constraint_programing(edges, edge_count, node_count):
    model = cp_model.CpModel()
    cvar = [model.NewIntVar(0,int(math.sqrt(2*edge_count)),str(i)) for i in range(node_count)]
    solution =[]
    for e in edges:
        model.Add(cvar[e[0]] != cvar[e[1]])
    count_color = int(math.sqrt(2*edge_count))+1
    start_time = time.time()
    while(1):
        end_time = time.time()
        if(int(end_time)-int(start_time) > 60*10):
            break
        for i in range(node_count):
            model.Add(cvar[i] < count_color)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60*5
        status = solver.Solve(model)
        if( status == cp_model.FEASIBLE):
            solution.clear()
            for i in range(node_count):
                solution.append( int(solver.Value(cvar[i])))
            count_color = max(solution) 
        else:
            break
    return count_color+1 , solution

def mixed_integer_programing(edges, edge_count, node_count):
    solver = pywraplp.Solver('solver_mip', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    max_count = int(math.sqrt(2*edge_count))+1
    # infinity = solver.infinity()
    # vertex i color j
    x = [[solver.IntVar(0,1,"x[%i][%i]" % (i,j)) for j in range(max_count)] for i in range(node_count) ]
    # color i used
    y = [solver.IntVar(0,1,"y[%i]" %i) for i in range(max_count) ]
    z = solver.IntVar(1,max_count,"z")
    for i in range(max_count):
        solver.Add(z >= (i+1)*y[i])
    for i in range(node_count):
        solver.Add(sum(x[i]) >= 1)
        solver.Add(sum(x[i]) <= 1)
    for (i1, i2) in edges:
        for j in range(max_count):
            solver.Add(x[i1][j]+x[i2][j]-y[j] <= 0)
    solver.Minimize(z)
    status = solver.Solve()
    
    # for i in range(count_color):

    if status == pywraplp.Solver.OPTIMAL:
        count_color = int(solver.Objective().Value())
        solution = []
        for i in range(node_count):
            for j in range(max_count):
                if(x[i][j].solution_value() > 0):
                    solution.append(j)
        
        return int(count_color), solution
    else:
        print('The problem does not have an optimal solution.')

# def greedy(edges, dege_count, node_count):
    

def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    # parse the input
    lines = input_data.split('\n')
    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
    
    # count_color, solution = mixed_integer_programing(edges, edge_count, node_count)
    # prepare the solution in the specified output format
    
    
    if node_count == 250 or node_count == 1000:
        local_search = TabuSearch()
        local_search.parameters(edges, node_count)
        max_count_color = int(math.sqrt(2*edge_count))+1
        count_color, solution = local_search.search(max_count_color, 100, 100000)
    else:
        count_color, solution = constraint_programing(edges, edge_count, node_count)
    output_data = str(count_color) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
        # solve_it(input_data)
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

