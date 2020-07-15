import numpy as np 
from numpy import linalg as la
from cv2 import cv2
D = np.zeros((1000, 128*128))
# matrix_image = np.zeros((1000, 128*128))
s = 0
#số hoá ảnh sang các vector 16k
for i in range(1000):
    image1 = cv2.imread("./data/"+ str(i) +".png" , 2)
    vector_image = []
    for j in range(128):
        vector_image.extend(image1[j])
    for j in range(128*128):
        s += vector_image[j]
        D[i][j] = vector_image[j]
#tính mean
avegrate = int(s/(1000*128*128))
#chuẩn hoá theo mean
for i in range(1000):
    for j in range(128*128):
        D[i][j] -= avegrate
#tìm ma trận hiệp biến 
U = (D.transpose()).dot(D)
print("Tim Được U")
#tìm trị riêng và vector riêng
eigenvalue, eigenvector = la.eig(U)
# Giữ lại 20 vector riêng tương ứng 20 trị riêng lớn nhất
print("done eigen")
id_max_values = []
for i in range(len(eigenvalue)):
    id_max_values.append(int(i))
def sort_rule(elem):
    return eigenvalue[elem]
id_max_values.sort(key = sort_rule, reverse= True)
_max_vectors = []
for i in range(20):
    t = id_max_values[i]
    _max_vectors.append(eigenvector[:,t])
max_vectors = np.array(_max_vectors)
max_vectors = max_vectors.transpose()
file_write = open("pca_place.txt", "w")
for i in range(128*128):
    for j in range(19):
        file_write.write(str(max_vectors[i][j]) + " ")
    file_write.write(str(max_vectors[i][19])+ "\n")

