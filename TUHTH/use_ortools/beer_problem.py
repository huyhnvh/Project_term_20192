from ortools.sat.python import cp_model
corn = [5, 15, 480]
hopes =[4, 4, 160]
malt = [35, 20, 1190]
profit =[13, 23]

model = cp_model.CpModel()
ale_var = model.NewIntVar(0,int(corn[2]/corn[0]),'av')
beer_var = model.NewIntVar(0,int(corn[2]/corn[1]),'bv')
model.Add (ale_var * corn[0] + beer_var * corn[1]<=corn[2])
model.Add (ale_var * hopes[0]+beer_var * hopes[1]<=hopes[2])
model.Add (ale_var * malt[0] + beer_var * malt[1]<=malt[2])
model.Maximize(profit[0] * ale_var + profit[1]*beer_var)
solver = cp_model.CpSolver()
status = solver.Solve(model)
if(status == cp_model.FEASIBLE):
    print(solver.Value(ale_var), " ", solver.Value(beer_var))