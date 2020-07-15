from ortools.sat.python import cp_model

model = cp_model.CpModel()
cvar = model.NewIntVar(0, )