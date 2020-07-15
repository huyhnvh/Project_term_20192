from ortools.sat.python import cp_model
import time
time_start = time.time()
model = cp_model.CpModel()
n = 200

cvar = [model.NewIntVar(0, n-1, str(i)) for i in range(n)]
model.AddAllDifferent(cvar)
model.Add(cvar[0] < int(n/2))
model.Add(cvar[-1] >= int(n/2))

diag1 =[]
diag2 =[]
for j in range(n):
    q1 = model.NewIntVar(0, 2 * n,str(j))
    diag1.append(q1)
    model.Add(q1 == cvar[j] + j)
    q2 = model.NewIntVar(-n, n, str(j))
    diag2.append(q2)
    model.Add(q2 == cvar[j] - j)
model.AddAllDifferent(diag1)
model.AddAllDifferent(diag2)
solver = cp_model.CpSolver()
status = solver.Solve(model)
time_end = time.time()
if status == cp_model.FEASIBLE:
    for i in range(n):
        print(solver.Value(cvar[i]), end=" ")
    print('\n', time_end-time_start)