from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score
from collections import namedtuple
from tqdm import tqdm
import numpy as np 
import math

def length(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 )

def linear_solver_ortools(customers_list_change,facility_list_change, setup_cost, capacity, demand, dist, facility_used):
    facility_count = len(facility_list_change)
    customer_count = len(customers_list_change)
    solver = pywraplp.Solver("solve_mip", pywraplp.Solver.CLP_LINEAR_PROGRAMMING)
    x = [[solver.IntVar(0,1,'[%i][%i]' %(i, j)) for j in range(customer_count)]for i in range(facility_count)]
    y = [solver.IntVar(0,1, "[%i]" %(i)) for i  in range(facility_count)]
    
    # add constraint 1
    constraint1 = [solver.Constraint(1,1) for j in range(customer_count)]
    for j in range(customer_count):
        for i in range(facility_count):
            constraint1[j].SetCoefficient(x[i][j], 1)
    # add constraint 2
    constraint2 = [solver.Constraint(0, capacity[i]) for i in facility_list_change]
    for i in range(facility_count):
        for j in range(customer_count):
            _j = customers_list_change[j]
            constraint2[i].SetCoefficient(x[i][j], demand[_j])
    # add constraint 3
    constraint3 = [[solver.Constraint(0,1) for j in range(customer_count)] for i in range(facility_count)]
    for i in range(facility_count):
        for j in range(customer_count):
            constraint3[i][j].SetCoefficient(y[i], 1)
            constraint3[i][j].SetCoefficient(x[i][j], -1)
    # add objective
    objt = solver.Objective()
    for i in range(facility_count):
        _i = facility_list_change[i]
        objt.SetCoefficient(y[i], setup_cost[_i])
        for j in range(customer_count):
            _j = customers_list_change[j]
            objt.SetCoefficient(x[i][j], dist[i][_j])
    objt.SetMinimization()
    status = solver.Solve()
    solution = [0 for j in range(customer_count)]
    obj = 0
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        obj = solver.Objective().Value()
        for j in range(customer_count):
            for i in range(facility_count):
                if(x[i][j].solution_value() > 0):
                    facility_used[i] = 1
                    solution[j] = facility_list_change[i]
                    break
    else :
        print("don't find solution!")
        return
    return solution, facility_used

def MIP_solver_ortools(customers_list_change,facility_list_change, setup_cost, capacity, demand, dist, facility_used):
    facility_count = len(facility_list_change)
    customer_count = len(customers_list_change)
    solver = pywraplp.Solver("solve_mip", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    x = [[solver.IntVar(0,1,'[%i][%i]' %(i, j)) for j in range(customer_count)]for i in range(facility_count)]
    y = [solver.IntVar(0,1, "[%i]" %(i)) for i  in range(facility_count)]
    
    # add constraint 1
    constraint1 = [solver.Constraint(1,1) for j in range(customer_count)]
    for j in range(customer_count):
        for i in range(facility_count):
            constraint1[j].SetCoefficient(x[i][j], 1)
    # add constraint 2
    constraint2 = [solver.Constraint(0, capacity[i]) for i in facility_list_change]
    for i in range(facility_count):
        for j in range(customer_count):
            _j = customers_list_change[j]
            constraint2[i].SetCoefficient(x[i][j], demand[_j])
    # add constraint 3
    constraint3 = [[solver.Constraint(0,1) for j in range(customer_count)] for i in range(facility_count)]
    for i in range(facility_count):
        for j in range(customer_count):
            constraint3[i][j].SetCoefficient(y[i], 1)
            constraint3[i][j].SetCoefficient(x[i][j], -1)
    # add objective
    objt = solver.Objective()
    for i in range(facility_count):
        _i = facility_list_change[i]
        if(facility_used[i] <1 ):
            objt.SetCoefficient(y[i], setup_cost[_i])
        for j in range(customer_count):
            _j = customers_list_change[j]
            objt.SetCoefficient(x[i][j], dist[i][_j])
    objt.SetMinimization()
    # run MIP and return solution if have optimal solution
    status = solver.Solve()
    solution = [0 for j in range(customer_count)]
    obj = 0
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        obj = solver.Objective().Value()
        for j in range(customer_count):
            for i in range(facility_count):
                if(x[i][j].solution_value() > 0):
                    facility_used[i] = 1
                    solution[j] = facility_list_change[i]
                    break
    else :
        print("don't find solution!")
        return
    return obj, solution, facility_used

# def k_mean_mix_mip(facility_point, customer_point,setup_cost, capacity, demand):
#     # dist facility - customer
#     customer_count = len(customer_point)
#     facility_count = len(facility_point)
#     dist = [[0 for j in range(customer_count)] for i in range(facility_count)]
#     for i in range(facility_count):
#         for j in range(customer_count):
#             dist[i][j] = length(facility_point[i], customer_point[j])
#     # cluster with k-mean
#     # min_score = 1<<20
#     # n = 0
#     # cluster_id = []
#     # for no_cluster in range(2,21):
#     #     kmean_model = KMeans(n_clusters=no_cluster, random_state=0).fit(facility_point)
#     #     _cluster_id = kmean_model.predict(facility_point)
#     #     score = davies_bouldin_score(facility_point, _cluster_id)
#     #     if(min_score > score):
#     #         min_score = score 
#     #         cluster_id = _cluster_id
#     #         n = no_cluster
#     # print(n)
#     # change_id_list = [[] for i in range(n)]
#     # for i in range(len(cluster_id)):
#     #     change_id_list[cluster_id[i]].append(i)
#     # for i in range(n):
#     #     print(len(change_id_list[i]))
#     no_cluster = 5
#     kmean_model = KMeans(n_clusters=no_cluster, random_state=0).fit(customer_point)
#     cluster_id_fac = kmean_model.predict(facility_point)
#     # kmean_model = KMeans(n_clusters=no_cluster, random_state=0).fit(customer_point)
#     cluster_id_cus = kmean_model.predict(customer_point)
#     change_id_list_cus = [[] for i in range(no_cluster)]
#     change_id_list_fac = [[] for i in range(no_cluster)]
#     for i in range(len(cluster_id_fac)):
#         change_id_list_fac[cluster_id_fac[i]].append(i)
#     for j in range(len(cluster_id_cus)):
#         change_id_list_cus[cluster_id_cus[j]].append(j)
#     solution = [0 for j in range(customer_count)]
#     obj = 0
#     for  i in range(no_cluster):
#         print("=============",len(change_id_list_fac[i]),"==================")
#         print("=============", len(change_id_list_cus[i]),"===================")
#         # print(len(setup_cost))
#         # print(len(capacity))
#         # print(len(demand))
#         # print(len(dist))
#         # print(len(facility_used))
#         if(len(change_id_list_cus[i]) > 0):
#             _obj, _solution =MIP_solver_ortools(change_id_list_cus[i],\
#                 change_id_list_fac[i],\
#                 setup_cost, capacity, demand, dist)
#             for j in range(len(change_id_list_cus[i])):
#                 solution[change_id_list_cus[i][j]] = _solution[j]
#             obj += _obj 
#     # facility_used = np.array(facility_used)
#     # setup_cost = np.array(setup_cost)
#     # obj += sum(facility_used*setup_cost)
#     # for j in range(customer_count):
#     #     obj += dist[solution[j]][j]
#     return obj, solution

def process_solution(solution, capacity, demand):
    facility_count = len(capacity)
    customer_count = len(demand)
    customers_list_change = []
    for j in range(customer_count):
        if(capacity[solution[j]] >= demand[j]):
            capacity[solution[j]] -= demand[j]
        else:
            customers_list_change.append(j)
    return customers_list_change, capacity


def load_input(input_data):
    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    facility_point = []
    customer_point = []
    setup_cost = []
    capacity = []
    demand = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        setup_cost.append(float(parts[0]))
        capacity.append(int(parts[1]))
        facility_point.append([float(parts[2]), float(parts[3])])

    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        demand.append(int(parts[0]))
        customer_point.append([float(parts[1]), float(parts[2])])
    dist = [[0 for j in range(customer_count)] for i in range(facility_count)]
    for i in range(facility_count):
        for j in range(customer_count):
            dist[i][j] = length(facility_point[i], customer_point[j])
    facility_used = [0 for i in range(facility_count)]
    solution, facility_used = linear_solver_ortools([j for j in range(customer_count)], [i for i in range(facility_count)], setup_cost, capacity, demand, dist, facility_used)
    customer_list_change, capacity = process_solution(solution, capacity, demand)
    obj, _solution, facility_used = MIP_solver_ortools(customer_list_change, [i for i in range(facility_count)], setup_cost, capacity, demand,  dist, facility_used)
    for i in range(len(_solution)):
        solution[customer_list_change[i]] = _solution[i]
    facility_used = np.array(facility_used)
    obj = 0
    setup_cost = np.array(setup_cost)
    obj += sum(facility_used*setup_cost)
    for j in range(customer_count):
        obj += dist[solution[j]][j]
    # if(facility_count*customer_count >= 100000):
    #     obj, solution = k_mean_mix_mip(facility_point, customer_point, setup_cost, capacity, demand)
    # else:
    #     customer_list_change = [i for i in range(customer_count)]
    #     facility_list_change = [i for i in range(facility_count)]
    #     obj, solution = MIP_solver_ortools(customer_list_change, facility_list_change,setup_cost, capacity, demand, dist)
    ######
    #######
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data
    
import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(load_input(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')