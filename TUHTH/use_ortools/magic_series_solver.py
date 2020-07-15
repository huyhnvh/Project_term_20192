from ortools.sat.python import cp_model

model = cp_model.CpModel()
n=5
Var = [model.NewIntVar(0,n-1, str(i)) for i in range(n)]

for i in range(n):
    count =0
    for var in Var:
        eq = model.NewBoolVar('eq')
        model.Add(var==i).OnlyEnforceIf(eq)
    model.Add(Var[i] == sum(eq)) 
solver = cp_model.CpSolver()
status = solver.Solve(model)
if status == cp_model.FEASIBLE:
    print (Var)           