#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
from sys import maxsize
import time 
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
import random
from local_search import GuidedLocalSearch

Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def greedy(nodes, nodeCount):
    path = [0 for i in range(nodeCount)]
    check_node = [False for i in range(nodeCount)]
    check_node[0] = True
    for i in range(nodeCount-1):
        Min = 1<<30
        for j in range(1,nodeCount):
            if(not(check_node[j])):
                l = length(nodes[path[i]], nodes[j])
                if(Min > l):
                    Min = l
                    path[i+1] = j
        check_node[path[i+1]] = True
    return path

def optimize2opt(nodes, solution, number_of_nodes):
    best = 0
    best_move = None
    # For all combinations of the nodes
    for ci in range(0, number_of_nodes):
        for xi in range(0, number_of_nodes):
            yi = (ci + 1) % number_of_nodes  # C is the node before Y
            zi = (xi + 1) % number_of_nodes  # Z is the node after X

            c = solution[ ci ]
            y = solution[ yi ]
            x = solution[ xi ]
            z = solution[ zi ]
            # Compute the lengths of the four edges.
            cy = length( nodes[c], nodes[y] )
            xz = length( nodes[x], nodes[z] )
            cx = length( nodes[c], nodes[x] )
            yz = length( nodes[y], nodes[z] )

            # Only makes sense if all nodes are distinct
            if xi != ci and xi != yi:
                # What will be the reduction in length.
                gain = (cy + xz) - (cx + yz)
                # Is is any better then best one sofar?
                if gain > best:
                    # Yup, remember the nodes involved
                    best_move = (ci,yi,xi,zi)
                    best = gain

    print (best_move, best)
    if best_move is not None:
        (ci,yi,xi,zi) = best_move
        # This four are needed for the animation later on.
        c = solution[ ci ]
        y = solution[ yi ]
        x = solution[ xi ]
        z = solution[ zi ]

        # Create an empty solution
        new_solution = [i for i in range(0, number_of_nodes)]
        # In the new solution C is the first node.
        # This we we only need two copy loops instead of three.
        new_solution[0] = solution[ci]

        n = 1
        # Copy all nodes between X and Y including X and Y
        # in reverse direction to the new solution
        while xi != yi:
            new_solution[n] = solution[xi]
            n = n + 1
            xi = (xi-1)%number_of_nodes
        new_solution[n] = solution[yi]

        n = n + 1
        # Copy all the nodes between Z and C in normal direction.
        while zi != ci:
            new_solution[n] = solution[zi]
            n = n + 1
            zi = (zi+1)%number_of_nodes
        # Create a new animation frame
        # frame4(nodes, new_solution, number_of_nodes, c, y, x, z, gain)
        return (True,new_solution)
    else:
        return (False,solution)

def two_opt_algorithm(nodes, number_of_nodes):
    # Create an initial solution
    solution = greedy(nodes, number_of_nodes)
    # solution = [0,10,7,16,77,42,96,50,12,55,98,39,68,24,41,57,91,38,80,29,5,46,53,14,75,15,19,71,43,65,37,2,28,67,73,87,48,85,33,59,21,70,23,8,66,64,60,81,94,40,47,72,26,9,11,84,35,76,61,69,6,58,56,4,32,83,78,95,92,52,63,20,90,49,97,79,88,45,27,1,54,86,82,25,62,44,31,93,51,3,89,13,18,22,99,34,17,30,74,36]
    # random.shuffle(solution)
    go = True
    # Try to optimize the solution with 2opt until
    # no further optimization is possible.
    while go:
        (go,solution) = optimize2opt(nodes, solution, number_of_nodes)
    return solution

def sa_optimize_step(nodes, solution, number_of_nodes, t):
    global nn 
    nn = 0
    # Pick X and Y at random.
    ci = random.randint(0, number_of_nodes-1)
    yi = (ci + 1) % number_of_nodes
    xi = random.randint(0, number_of_nodes-1)
    zi = (xi + 1) % number_of_nodes

    if xi != ci and xi != yi:
        c = solution[ci]
        y = solution[yi]
        x = solution[xi]
        z = solution[zi]
        cy = length( nodes[c], nodes[y] )
        xz = length( nodes[x], nodes[z] )
        cx = length( nodes[c], nodes[x] )
        yz = length( nodes[y], nodes[z] )

        gain = (cy + xz) - (cx + yz)
        if gain < 0:
            # We only accept a negative gain conditionally
            # The probability is based on the magnitude of the gain
            # and the temperature.
            u = math.exp( gain / t )
        elif gain > 0.05:
            u = 1 # always except a good gain.
        else:
            u = 0 # No idea why I did this....

        # random chance, picks a number in [0,1)
        if (random.random() < u):
            nn = nn + 1
            new_solution = [i for i in range(0,number_of_nodes)]
            new_solution[0] = solution[ci]
            n = 1
            while xi != yi:
                new_solution[n] = solution[xi]
                n = n + 1
                xi = (xi-1)%number_of_nodes
            new_solution[n] = solution[yi]
            n = n + 1
            while zi != ci:
                new_solution[n] = solution[zi]
                n = n + 1
                zi = (zi+1)%number_of_nodes

            return new_solution
        else:
            return solution
    else:
        return solution

def total_length( nodes, solution ):
    cost = length(nodes[solution[0]], nodes[solution[-1]])
    for i in range(1,len(solution)):
        cost += length(nodes[solution[i-1]], nodes[solution[i]])
    return cost

def sa_algorithm(nodes, number_of_nodes):
    # Create an initial solution that we can improve upon.
    solution = greedy(nodes, number_of_nodes)
    t = 200
    # Length of the best solution so far.
    l_min = total_length( nodes, solution )
    best_solution = []
    i = 0
    while t > 0.1:
        i = i + 1
        # Given a solution we create a new solution
        solution = sa_optimize_step(nodes, solution, number_of_nodes, t)
        # every ~200 steps
        if i >= 200:
            i = 0
            # Compute the length of the solution
            l = total_length( nodes, solution )
            print ("    ", l, t, nn)
            # Lower the temperature.
            # The slower we do this, the better then final solution
            # but also the more times it takes.
            t = t*0.9995

            # See if current solution is a better solution then the previous
            # best one.
            if l_min is None: # TODO: This can be removed, as l_min is set above.
                l_min = l
            elif l < l_min:
                # Yup it is, remember it.
                l_min = l
                print ("++", l, t)
                best_solution = solution[:]
            else:
                pass

    return best_solution

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])
    nodes = []
    
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        nodes.append(Point(float(parts[0]), float(parts[1])))
    start_time = time.time()
    # solution = two_opt_algorithm(nodes, nodeCount)
    # solution = sa_algorithm(nodes, nodeCount)
    # solution = greedy(nodes, nodeCount)
    # best_cost = length(nodes[solution[0]], nodes[solution[-1]])
    # for i in range(1,nodeCount):
    #     best_cost += length(nodes[solution[i-1]], nodes[solution[i]])
    local_search = GuidedLocalSearch()
    local_search.parameters(nodes, nodeCount)
    if nodeCount <1000:
        best_cost, solution = local_search.search(10000)
    elif nodeCount < 2000:
        best_cost, solution = local_search.search(50000)
    else:
        best_cost, solution = local_search.search(1000000)

    output_data = '%.2f' % best_cost + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))
    return output_data

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

