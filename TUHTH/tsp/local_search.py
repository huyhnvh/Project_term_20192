from collections import namedtuple
import math
import random

Point = namedtuple("Point", ['x', 'y'])
def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

class GuidedLocalSearch:
    def __init__(self):
        self.l = 0.1
        self.penalties = []
        self.initial_solution = []
        self.distance_matrix = []
        self.bits = []
        self.t = 0

    def greedy(self, nodes, node_count):
        path = [0 for i in range(node_count)]
        check_node = [False for i in range(node_count)]
        check_node[0] = True
        for i in range(node_count-1):
            Min = 1<<30
            for j in range(1,node_count):
                if(not(check_node[j])):
                    l = length(nodes[path[i]], nodes[j])
                    if(Min > l):
                        Min = l
                        path[i+1] = j
            check_node[path[i+1]] = True
        return path
    
    def parameters(self, nodes, node_count):
        self.penalties= [[0 for i in range(node_count)] for i in range(node_count)]
        if(node_count < 2000):
            self.initial_solution = self.greedy(nodes, node_count)
        else:
            self.initial_solution = [i for i in range(node_count)]
            random.shuffle(self.initial_solution)
        self.distance_matrix = [[0 for i in range(node_count)] for i in range(node_count)]
        self.bits.extend([0 for i in range(node_count)])
        for i in range(node_count-1):
            for j in range(i+1, node_count):
                self.distance_matrix[i][j] = length(nodes[i], nodes[j])
                self.distance_matrix[j][i] = self.distance_matrix[i][j]

    def total_distance(self, path):
        sumd = 0
        for i in range(len(path)):
            sumd += self.distance_matrix[path[i-1]][path[i]]
        return sumd

    def augmented_obj_func(self, path, t1, t2, t3, t4):
        d12 = self.distance_matrix[path[t1]][path[t2]]
        d34 = self.distance_matrix[path[t3]][path[t4]]
        d13 = self.distance_matrix[path[t1]][path[t3]]
        d24 = self.distance_matrix[path[t2]][path[t4]]
        p12 = self.penalties[path[t1]][path[t2]]
        p34 = self.penalties[path[t3]][path[t4]]
        p13 = self.penalties[path[t1]][path[t3]]
        p24 = self.penalties[path[t2]][path[t4]]
        return (d12+d34-d24-d13) + self.l*(p12+p34-p13-p24)

    def update_panalties(self, path):
        max_util = -1<<20
        max_util_nodes = []
        for i in range(len(path)):
            i_out = (i+1)%len(path)
            dis_val = self.distance_matrix[path[i]][path[i_out]]
            pen_val = self.penalties[path[i]][path[i_out]]
            util = dis_val/(pen_val+1)

            if max_util < util:
                max_util = util
                max_util_nodes.clear()
                max_util_nodes.append(i)
            elif max_util == util:
                max_util_nodes.append(i)
        for i in max_util_nodes:
            i_out = (i+1)%len(path)
            self.penalties[path[i]][path[i_out]] += 1
            self.penalties[path[i_out]][path[i]] += 1
            self.bits[path[i]] = 1
            self.bits[path[i_out]] = 1
    
    def compute_lambda(self, path):
        return 0.1*self.total_distance(path) / len(path)

    def creat_new_path(self, path, t2, t3):
        low = t2 
        high = t3
        if t2 > t3 :
            low = t2 - len(path)
        for i in range(int((high-low+1)/2)):
            sw = path[i+low]
            path[i+low] = path[high-i]
            path[high-i] = sw 
        return path 

    def two_opt_move(self, index, path):
        size_path = len(path)
        candidate_t3 = []
        for i in range(2):
            max_gain = - 1<<20
            if i == 0:
                t1 = (index -1 + size_path)%size_path
                t2 = index
            else:
                t1 = index
                t2 = (index+1)%size_path
            for j in range(size_path):
                t3 = j 
                t4 = (t3+1)%size_path
                if path[t4] == path[t1] or path[t4] == path[t2] or path[t3] == path[t2]:
                    continue
                gain = self.augmented_obj_func(path, t1,t2,t3,t4)
                if max_gain < gain:
                    max_gain = gain
                    candidate_t3.clear()
                    candidate_t3.append(t3)
                elif max_gain == gain:
                    candidate_t3.append(t3)
            if max_gain > 1e-6:
                t3 = random.choice(candidate_t3)
                t4 = (t3+1)%size_path
                self.bits[path[t1]] = 1
                self.bits[path[t2]] = 1
                self.bits[path[t3]] = 1
                self.bits[path[t4]] = 1
                return self.creat_new_path(path, t2, t3)
            elif i == 1:
                self.bits[path[index]] = 0
                return path
            
    def search(self, max_step):
        solution = self.initial_solution
        # print(len(solution))
        best_solution =[] 
        best_solution.extend(solution )
        min_total_distance = self.total_distance(best_solution)
        self.l = 0
        
        for self.t in range(max_step):
            # print("step: ", self.t, "   total distance: ", min_total_distance, "sum bits: ", sum(self.bits))
            while(sum(self.bits) > 0):
                for i in range(len(solution)):
                    if self.bits[solution[i]] == 0:
                        continue
                    solution = self.two_opt_move(i, solution)
                    current_total_distance = self.total_distance(solution)
                    # if self.t == 354:
                    #     print(current_total_distance)
                    if min_total_distance > current_total_distance:
                        min_total_distance = current_total_distance
                        best_solution.clear()
                        best_solution.extend(solution)
            if self.l == 0:
                self.l = self.compute_lambda(solution)
            self.update_panalties(solution)
        return min_total_distance, best_solution                

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
    # best_cost = length(nodes[solution[0]], nodes[solution[-1]])
    # for i in range(1,nodeCount):
    #     best_cost += length(nodes[solution[i-1]], nodes[solution[i]])
    local_search = GuidedLocalSearch()
    local_search.parameters(nodes, nodeCount)
    best_cost, solution = local_search.search(10000)
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



