import random
import math

class TabuSearch:
    def __init__(self):
        self.conection_matrix = []
        self.node_count = 0
        self.tabu_size = 0
        self.tabu_list = []
        self.conflict = []
    
    def parameters(self, edges, nodeCount):
        self.node_count = nodeCount
        self.conection_matrix = [[0 for i in range(nodeCount)]for i in range(nodeCount)]
        for i in range(len(edges)):
            self.conection_matrix[edges[i][0]][edges[i][1]] = 1
            self.conection_matrix[edges[i][1]][edges[i][0]] = 1
        self.tabu_size = int(nodeCount/10)
    
    def generate_init_solution(self, k):
        init_sol = []
        for i in range(self.node_count):
            init_sol.append(random.choice(range(k)))
        return init_sol

    def compute_conflict(self, sol):
        self.conflict = [0 for i in range(self.node_count)]
        for i in range(self.node_count - 1):
            for j in range(1, self.node_count):
                if self.conection_matrix[i][j] > 0 and sol[i] == sol[j]:
                    self.conflict[i] += 1
                    self.conflict[j] += 1
        print(sum(self.conflict))
        
    def find_candidate_node(self, sol):
        candidates = []
        max_conflict = -1
        check = True
        while(check):
            for i in range(self.node_count):
                if i in self.tabu_list:
                    continue
                if max_conflict < self.conflict[i]:
                    max_conflict = self.conflict[i]
                    candidates.clear()
                    candidates.append(i)
                elif max_conflict == self.conflict[i]:
                    candidates.append(i)
            if len(candidates) > 0:
                check = False
            else:
                self.tabu_list.pop(0)
        return random.choice(candidates)
    
    def set_color(self,node, sol):
        color_used = [0 for i in range(int(max(sol))+1)]
        for i in range(self.node_count):
            if self.conection_matrix[node][i] >0:
                color_used[sol[i]] += 1
        color_least_used = []
        least_value = 1<<20
        for i in range(len(color_used)):
            if i == sol[node]:
                continue
            if least_value > color_used[i]:
                least_value = color_used[i]
                color_least_used.clear()
                color_least_used.append(i)
            elif least_value == color_used[i]:
                color_least_used.append(i)
        if len(color_least_used) == 0:
            return [], []
        choice_color = random.choice(color_least_used)
        for i in range(self.node_count):
            if self.conection_matrix[node][i] >0:
                if sol[i] == sol[node]:
                    self.conflict[i] -= 1
                    self.conflict[node] -= 1
                elif sol[i] == choice_color:
                    self.conflict[i] += 1
                    self.conflict[node] += 1
        sol[node] = choice_color
        return sol

    def print_solution(self, sol):
        s = str(max(sol)+1) + ' ' + str(0) + '\n'
        s += ' '.join(map(str, sol))
        print(s)
        return

    def search(self, max_color, max_iter, max_step):
        best_solution = []
        # for k in range(5, max_color)[::-1]:
        k = max_color
        while k > 5:
            current_solution = self.generate_init_solution(k)
            it = 0
            while (1):
                self.compute_conflict(current_solution)
                # print(conflict)
                step = 0
                while(step < max_step and sum(self.conflict) > 0):
                    node = self.find_candidate_node(current_solution)
                    self.tabu_list.append(node)
                    if len(self.tabu_list) > self.tabu_size:
                        self.tabu_list.pop(0)
                    current_solution = self.set_color(node, current_solution)
                    if len(current_solution)==0:
                        return max(best_solution) +1, best_solution
                    step += 1
                if sum(self.conflict) == 0:
                    best_solution.clear()
                    best_solution.extend(current_solution)
                    self.print_solution(best_solution)
                    k = max(best_solution)+1
                    break
                it += 1
                if it > max_iter:
                    break
            k -= 1
                
        return max(best_solution) +1, best_solution

def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    # parse the input
    lines = input_data.split('\n')
    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])
    max_count_color = int(math.sqrt(2*edge_count))+1
    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
    local_search = TabuSearch()
    local_search.parameters(edges, node_count)
    count_color, solution = local_search.search(max_count_color, 100, 10000) 
    output_data = str(count_color) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    # print(node_count)
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
