import random
import math
from collections import namedtuple

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

class GuidedLocalSearch:
    def __init__(self):
        self.penalty = []
        self.initial_solution = []
        self.feature = []
        self.alpha = 0.05
        self.lam = 0.0
        self.limit = 100000
        self.distance_matrix = []
        self.available = []
        self.facilities = []
        self.cus_of_fa = []
        self.customers = []

    def length(self, point1, point2):
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

    def setup_parameters(self):
        self.distance_matrix = [[0 for j in range(len(self.facilities))]for i in range(len(self.customers))]
        self.feature = [[0 for j in range(len(self.facilities))]for i in range(len(self.customers))]
        self.available = [self.facilities[i].capacity for i in range(len(self.facilities))]
        self.cus_of_fa = [0 for i in range(len(self.facilities))]
        for i in range(len(self.customers)):
            for j in range(len(self.facilities)):
                self.distance_matrix[i][j] = self.length(self.customers[i].location, self.facilities[j].location)
                self.feature[i][j] = self.facilities[j].setup_cost
    
    def find_initial_solution(self):
        self.initial_solution = [0 for i in range(len(self.customers))]
        for i in range(len(self.customers)):
            min_distance = 1<<40
            min_facility = -1
            for j in range(len(self.facilities)):
                if min_distance > self.distance_matrix[i][j] and self.customers[i].demand < self.available[j]:
                    min_distance = self.distance_matrix[i][j]
                    min_facility = j 
            self.initial_solution[i] = min_facility
            self.available[min_facility] -= self.customers[i].demand
            self.cus_of_fa[min_facility] += 1

    def get_cost(self):
        cost = 0
        for i in range(len(self.initial_solution)):
            cost += self.distance_matrix[i][self.initial_solution[i]]
        for i in range(len(self.cus_of_fa)):
            if self.cus_of_fa[i] > 0:
                cost += self.facilities[i].setup_cost
        return cost 
    
    def get_augmented_cost(self):
        augmented_cost = 0
        for i in range(len(self.initial_solution)):
            augmented_cost += self.distance_matrix[i][self.initial_solution[i]] + self.lam * self.penalty[i][self.initial_solution[i]] 
        for i in range(len(self.cus_of_fa)):
            if self.cus_of_fa[i] > 0:
                augmented_cost += self.facilities[i].setup_cost
        return augmented_cost 

    def compute_lambda(self, cost):
        self.lam = self.alpha*cost / len(self.customers)

    def customer_move(self):
        max_gain = -(1<<20)
        candidates_cus = []
        candidates_fa = []
        for i in range(len(self.customers)):
            for j in range(len(self.facilities)):
                if j == self.initial_solution[i] :
                    continue
                if self.available[j] < self.customers[i].demand:
                    continue
                augmented_cost_old = self.distance_matrix[i][self.initial_solution[i]] + self.lam * self.penalty[i][self.initial_solution[i]]
                if self.cus_of_fa[self.initial_solution[i]] == 1:
                    augmented_cost_old += self.lam*self.facilities[self.initial_solution[i]].setup_cost
                augmented_cost_new = self.distance_matrix[i][j] + self.lam * self.penalty[i][j]
                if self.cus_of_fa[j] == 0:
                    augmented_cost_new += self.lam * self.facilities[j].setup_cost
                gain = augmented_cost_old - augmented_cost_new
                if gain > max_gain:
                    candidates_cus.clear()
                    candidates_fa.clear()
                    candidates_cus.append(i)
                    candidates_fa.append(j)
                    max_gain = gain 
                elif gain == max_gain:
                    candidates_cus.append(i)
                    candidates_fa.append(j)
        if max_gain > 0:
            id = random.choice(range(len(candidates_cus)))
            return (max_gain, candidates_cus[id], self.initial_solution[candidates_cus[id]], candidates_fa[id] )
        else:
            return (max_gain, 0, 0, 0)

    def update_panalty(self, augmented_cost):
        max_util = -(1<<20)
        ac = augmented_cost
        list_customer = []
        for i in range(len(self.customers)):
            util = self.feature[i][self.initial_solution[i]]/(1+self.penalty[i][self.initial_solution[i]])
            if max_util < util:
                max_util = util
                list_customer.clear()
                list_customer.append(i)
            elif max_util == util:
                list_customer.append(i)
        for i in list_customer:
            self.penalty[i][self.initial_solution[i]] += 1
            ac += self.lam
        return ac 

    def search(self, facilities, customers):
        f = open('guided_result_'+str(len(facilities))+'_'+str(len(customers)), 'w')
        self.facilities = facilities
        self.customers = customers
        self.setup_parameters()
        self.find_initial_solution()
        cost = self.get_cost()
        self.penalty = [[0 for i in range(len(self.facilities))] for j in range(len(self.customers))]
        augmented_cost = self.get_augmented_cost()
        best_cost = cost
        best_augmented_cost = augmented_cost
        best_solution = []
        best_solution.extend(self.initial_solution)
        for t in range(15000):
            if t%500 == 0:
                output_data = '%.2f' % best_cost + ' ' + str(0) + '\n'
                output_data += ' '.join(map(str, best_solution))
                f.write(output_data+'\n')
            print ("time: ",t ,"  cost: ", best_cost, " best augented_cost: ", best_augmented_cost )
            (gain, customer_id_move, facility_old, facility_new) = self.customer_move()
            print (gain, customer_id_move, facility_old, facility_new)
            if gain <= 0 :
                if self.lam == 0:
                    self.compute_lambda(cost)
                augmented_cost = self.update_panalty(augmented_cost)
                print(augmented_cost)
            else:
                cost_old = self.distance_matrix[customer_id_move][facility_old]
                if self.cus_of_fa[facility_old] == 1:
                    cost_old += self.facilities[facility_old].setup_cost
                cost_new = self.distance_matrix[customer_id_move][facility_new]
                if self.cus_of_fa[facility_new] == 0:
                    cost_new += self.facilities[facility_new].setup_cost
                cost -= (cost_old -cost_new)
                print(cost)
                # cost = self.get_cost()
                augmented_cost = self.get_augmented_cost()
                self.available[facility_old] += self.customers[customer_id_move].demand
                self.cus_of_fa[facility_old] -= 1
                self.available[facility_new] -= self.customers[customer_id_move].demand
                self.cus_of_fa[facility_new] += 1
                self.initial_solution[customer_id_move] = facility_new
            if (cost < 0):
                break
            if best_cost > cost :
                best_cost = cost
                best_augmented_cost = augmented_cost
                best_solution.clear()
                best_solution.extend(self.initial_solution)
                best_cost = self.get_cost()
        return best_cost, best_solution

    