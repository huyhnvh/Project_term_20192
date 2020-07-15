from fractions import Fraction as F 
import numpy as np 

a = np.array([0,0,0])
b =np.array([[1,2,3], [2,3,4]])
b[0] = a 
print(b)