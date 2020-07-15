import numpy as np 
import matplotlib
from gym import spaces
from tqdm import tqdm 
import itertools
import math
import matplotlib.pyplot as plt 

class Solver:
    def __init__(self):
        self._timeslot = 0.25  # khe thời gian t
        self._batery_capacity = 2000  # ngưỡng pin
        self._server_service_rate = 20 # tỷ lệ xử lý ở sever units/s
        self._lamda_high = 100 # só đơn vị công việc đến / s (max)
        self._lamda_low = 10 
        self._b_high = self._batery_capacity/self._timeslot # năng lượng pin max
        self._b_low = 0
        self._h_high = 0.06*5 # khắc phục s/unit
        self._h_low = 0.02*5
        self._e_high = 2 # trạng thái môi trường
        self._e_low = 0
        self._back_up_cost_coef = 0.15
        self._normalized_unit_depreciation_cost = 0.01
        self._max_number_of_server = 15
        self._priority_coefficent = 0.95
        self._delta = 0.9
        self._learnng_rate = 0.9995
        self._alpha = 0.9
        self._r_high = np.array([self._lamda_high, self._b_high, self._h_high, self._e_high])
        self._r_low = np.array([self._lamda_low, self._b_low, self._h_low, self._e_low])
        self._observation_space = spaces.Box(low=self._r_low, high=self._r_high) # kg quan sát
        self._action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32) # kg hành động
        self._zip_space = zip(itertools.repeat(self._observation_space), itertools.repeat(self._action_space))
        # self._cost_exp = {0 for (s,a) in self._zip_space}
        # self._normal_value = {0.0 for s in self._observation_space.shape[0]}
        # self._pds_value = {0.0 for s in self._observation_space.shape[0]}
        # power
        self._d_sta = 300
        self._coef_dyn = 0.5
        self._server_power_consumption = 150
        # time
        self._time_steps_per_episode = 96
        self._episode = 0
        self._state = [0, 0, 0, 0]
        self._time = 0
        self._time_step = 0
        # work
        self._d_op = 0
        self._d_com = 0
        self._d = 0
        self._m = 0
        self._mu = 0
        self._g = 0
        # cost ... 
        self._reward_time = 0
        self._reward_bak = 0
        self._reward_bat = 0
    def state_reset(self):
        self._time = 0
        self._time_step = 0
        self._state = np.array([self._lamda_low, self._b_high, self._h_low, self._e_low])
        return self._state

    def get_dop(self,state):
        return self._d_sta + self._coef_dyn*state[0]

    def get_dcom(self, m, muy):
        return self._server_power_consumption*m +self._server_power_consumption*muy/self._lamda_low

    def check_constraints(self, m, mu, state):
        if mu > state[0] or mu < 0: return False
        if isinstance(self._mu, complex): return False
        if m * self._server_service_rate <= mu: return False
        return True
    
    def cost_delay_local_function(self, m, mu):
        if m == 0 and mu == 0: return 0
        return mu / (m * self._server_service_rate - mu)
    
    def cost_delay_cloud_function(self, mu, h, lamda):
        return (lamda - mu) * h
    
    def cost_function(self, m, mu, h, lamda):
        return self.cost_delay_local_function(m, mu) + self.cost_delay_cloud_function(mu, h, lamda)
   
    def get_m_mu(self, de_action, state):
        lamda, _1, h, _2 = state 
        opt_val = math.inf
        ans = [-1, -1]
        for m in range(1, self._max_number_of_server + 1):
            normalized_min_cov = self._lamda_low
            mu = (de_action - self._server_power_consumption * m) * normalized_min_cov / self._server_power_consumption
            valid = self.check_constraints(m, mu,state)
            if valid:
                if self.cost_function(m, mu, h, lamda) < opt_val:
                    ans = [m, mu]
                    opt_val = self.cost_function(m, mu, h, lamda)
        return ans
    
    def cal(self, action, state):
        lamda, b, h, _ = state
        d_op = self.get_dop(state)
        if b <= d_op + 150:
            return [0, 0]
        else:
            low_bound = 150
            high_bound = np.minimum(b - d_op, self.get_dcom(self._max_number_of_server,lamda))
            de_action = low_bound + action * (high_bound - low_bound)
            return self.get_m_mu(de_action, state)
    
    def reward_func(self, action, state):
        lamda, b, h, _ = state
        self._m, self._mu = self.cal(action,state)
        cost_delay = self.cost_function(self._m, self._mu,h,lamda)
        if (self._d_op > b):
            cost_batery = 0
            cost_bak = self._back_up_cost_coef * self._d_op
        else:
            cost_batery = 0.01*max(self._d - self._g, 0)
            cost_bak =0
        cost = 0.5*cost_bak + 0.5*cost_batery + 0.5*cost_delay
        return cost

    def get_time(self):
        self._time += 0.25
        if self._time == 24:
            self._time = 0

    def get_g(self, state):
        e = state[3]
        if e == 0:
            # return np.random.exponential(60) + 100
            return np.random.normal(200,100)
        if e == 1:
            # return np.random.normal(520, 130)
            return np.random.normal(400, 100)
        return np.random.normal(800, 95)

    def get_b(self, state):
        b = state[1]
        # print('\t', end = '')
        if self._d_op > b:
            # print('unused batery')
            return b + self._g
        else:
            if self._g >= self._d:
                # print('recharge batery')
                return np.minimum(self._b_high, b + self._g - self._d)
            else:
                # print('discharge batery')
                return b + self._g - self._d

    def get_e(self):
        if self._time >= 9 and self._time < 15:
            return 2
        if self._time < 6 or self._time >= 18:
            return 0
        return 1


    def step(self, action, state):
        done = True
        self.get_time()
        self._time_step += 1
        self._g = self.get_g(state)
        self._d_op = self.get_dop(state)
        self._m, self._mu = self.cal(action, state)
        self._d_com = self.get_dcom(self._m, self._mu)
        self._d = self._d_op +self._d_com
        reward = self.reward_func(action, state)
        lamda_t = np.random.choice(range(1,11))*10
        b_t = int(self.get_b(state)/100) * 100
        h_t = np.random.choice(range(2,7))*0.05
        e_t = self.get_e()
        state = np.array([lamda_t, b_t, h_t,e_t])
        if  self._time_step >= self._time_steps_per_episode:
            self.state_reset()
            done = False
        return state, reward, done
    
    def behavior_policy(self, state,state_action_values,state_action_pair_count):
        # cost_min = int(1e9)
        # action_choice = -1
        # for a in range(101):
        #     action = a*0.01
        #     c = self.reward_func(action, state)
        #     if(c < cost_min):
        #         action_choice = action
        #         cost_min = c
        lamda, b, h, e = state
        lamda =int(lamda/10- 1)
        h = int(h/0.05) - 2
        b = int(b/100) 
        e = int(e)
        action_min = np.random.choice(range(0,11))
        v_min = 1<<13
        for i in range(0,11):
            if(state_action_pair_count[lamda, b, h, e, i] > 0):
                avg = state_action_values[lamda, b, h, e, i]/state_action_pair_count[lamda, b, h, e, i]
                if(avg < v_min):
                    action_min = i
                    v_min = avg
        return  action_min/10

    def process(self, initial_state, initial_action,state_action_values,state_action_pair_count):
        done = True
        state = initial_state
        reward_list = []
        trajectory_list = []
        i = 0
        # avg_reward_list = []
        while(done):
            if(i == 0):
                action = initial_action
            else:
                action = self.behavior_policy(state,state_action_values,state_action_pair_count)
            trajectory_list.append([(state[0], state[1], state[2],state[3]), action])
            state, r, done = self.step(action, state)
            reward_list.append(r)
            i += 1

            # avg_reward_list.append(np.mean(reward_list[:]))
        return reward_list ,trajectory_list
    
    def random_zero_state_action(self,state_action_pair_count):
        list_random = []
        for s_lamda in range(10):
            for s_b in range(81):
                for s_h in range(5):
                    for s_e in range(3):
                        for initial_action in range(11):
                            if(state_action_pair_count[s_lamda, s_b, s_h, s_e, initial_action] == 0 ):
                                list_random.append([s_lamda, s_b, s_h, s_e, initial_action])
        if(len(list_random) > 0):
            random_array = list_random[np.random.choice(range(len(list_random)))]
            s_lamda = random_array[0]
            s_b = random_array[1]
            s_h = random_array[2]
            s_e = random_array[3]
            initial_action = random_array[4]
            s_lamda = (s_lamda+1)*10
            s_b *= 100
            s_h = (s_h+2)*0.05
            initial_action /= 10
            initial_state = [s_lamda, s_b, s_h, s_e]
        else:
            initial_state = [np.random.choice(range(1,11))*10, np.random.choice(range(81))*100, np.random.choice(range(2,7))*0.05, np.random.choice(range(3))]
            initial_action = np.random.choice(range(11)) * 0.1
        return initial_state, initial_action

    def monte_carlo_es(self, episodes):
        self._action_space
        self._observation_space.shape[0]
        state_action_values = np.zeros((10, 81, 5, 3, 11))
        state_action_pair_count = np.zeros((10, 81, 5, 3, 11))
        print(enumerate(state_action_pair_count))
        avg_reward_day = []
        avg_reward = []
        for k in tqdm(range(episodes)):
            # (s_lamda,s_b,s_h,s_e,initial_action) =  np.random.choice([(s_lamda,s_b,s_h,s_e,initial_action) for (s_lamda,s_b,s_h,s_e,initial_action), value_ in enumerate(state_action_pair_count) if value_ == np.min(state_action_pair_count)])
            
            # initial_state = [s_lamda,s_b,s_h,s_e]
            # initial_state, initial_action = self.random_zero_state_action(state_action_pair_count)
            initial_state = [np.random.choice(range(1,11))*10, np.random.choice(range(81))*100, np.random.choice(range(2,7))*0.05, np.random.choice(range(3))]
            initial_action = np.random.choice(range(11)) * 0.1
            reward, trajectory = self.process(initial_state, initial_action,state_action_values,state_action_pair_count)
            first_visit_check = set()
            j = 0
            for (lamda, b, h, e), action in trajectory:
                lamda =int(lamda/10- 1)
                h = int(h/0.05) - 2
                b = int(b/100)
                e = int(e)
                state_action = (lamda, b, h, e, action)
                if state_action in first_visit_check:
                    continue
                first_visit_check.add(state_action)
                a_integer = int(action*10)
                state_action_values[lamda, b, h, e, a_integer] += reward[j]
                j += 1
                state_action_pair_count[lamda, b, h, e, a_integer] += 1
            avg_reward_day.append(sum(reward)/96)
            avg_reward.append(np.mean(avg_reward_day))
        f = open("monte_carlo_reward.csv", 'w')
        for i in range(2000):
            f.write(str(avg_reward[i]) +"\n") 
        f.close()
        return state_action_values/state_action_pair_count, avg_reward


solver = Solver()
_,avg_reward_day = solver.monte_carlo_es(10000)
# 1000
plt.plot([avg_reward_day[i] for i in range(1000)], label = "avg cost in day")
plt.xlabel('Episodes (log scale)')
plt.ylabel('Mean cost (W)')
plt.xscale('log')
plt.legend()
plt.savefig('figure_oa_1000.png')
plt.close()
# 10000
plt.plot(avg_reward_day,label = "avg cost in day")
plt.xlabel('Episodes (log scale)')
plt.ylabel('Mean cost (W)')
plt.xscale('log')
plt.legend()
plt.savefig('figure_oa_10000.png')
plt.close()