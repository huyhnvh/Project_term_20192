#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i, int(parts[0]), int(parts[1])))

    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    value = 0
    #weight = 0
    taken = [0]*len(items)
    arr_val = [[0 for i in range(capacity+1)] for i in range(2)]
    arr_take = [["" for i in range(capacity+1)] for i in range(2)]
    for item in items:
        i = item.index % 2
        for w in range(capacity+1):
            if  w == 0:
                arr_val[i][w] = 0
            elif item.weight <= w:
                arr_val[i][w] = max(item.value + arr_val[abs(i-1)][w - item.weight], arr_val[abs(i-1)][w])
            else:
                arr_val[i][w] = arr_val[abs(i-1)][w]
            if(arr_val[i][w] > arr_val[abs(i-1)][w]):
                    arr_take[i][w] =arr_take[abs(i-1)][w-item.weight] +" "+ str(item.index) 
            else:
                arr_take[i][w] =arr_take[abs(i-1)][w]
        
    value = arr_val[(item_count)%2][capacity]
    take_nums = arr_take[item_count%2][capacity].split()
    for take_num in take_nums:
        taken[int(take_num)-1] = 1
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

