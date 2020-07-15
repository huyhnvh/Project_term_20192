#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import namedtuple
import sys
from ortools.sat.python import cp_model
Item = namedtuple("Item", ['index', 'value', 'weight'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []
    items.append(Item(0,0,0))
    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i, int(parts[0]), int(parts[1])))

    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    value = 0
    model = cp_model.CpModel()
    or_taken =[ model.NewIntVar(0,1,str(i))for i in range(item_count)]
    or_weight = []
    or_value = []
    or_sum_weight = model.NewIntVar(0, capacity, 'os')
    or_sum_value = model.NewIntVar(0, 1<<40, 'ov')
    for i in range(item_count):
        t = or_taken[i]
        vbool = model.NewBoolVar('vb ')
        model.Add(t == 1).OnlyEnforceIf(vbool)
        model.Add(t != 1).OnlyEnforceIf(vbool.Not())
        or_weight.append(vbool * int(items[i+1].weight))
        or_value.append(vbool*int(items[i+1].value))
    model.Add(or_sum_weight == sum(or_weight))
    model.Add(or_sum_value == sum(or_value))
    model.Add(or_sum_weight <= capacity)
    value =0
    taken = []
    while(1):
        model.Add(or_sum_value > value)
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if (status == cp_model.FEASIBLE):
            taken.clear()
            value = solver.Value(or_sum_value)
            for i in range(item_count):
                taken.append(int(solver.Value(or_taken[i])))
        else:
            break
   
    #*tham lam*
    # def bool_sort(x):
    #     return x.value/x.weight
    # items.sort(key=bool_sort, reverse=True)
    # taken =[0 for i in range(item_count)]
    # current_weight = capacity
    # for i in range(item_count):
    #     if(items[i].weight<=current_weight):
    #         value += items[i].value
    #         current_weight -= items[i].weight
    #         taken[items[i].index -1 ] =1

    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')