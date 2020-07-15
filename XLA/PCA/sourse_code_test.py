import numpy as np 
from cv2 import cv2 
import math

#load vào ma trận không gian pca
file = open("pca_place.txt", "r")
lines = file.readlines()
_pca = []
for line in lines:
    list_load = line.split()
    list_f = []
    for l in list_load:
        if(l != ''):
            list_f.append(float(l))
    if(list_f != []):
        _pca.append(list_f)
pca = np.array(_pca)
image_save = []
#số hoá 1000 ảnh
matrix_image = np.zeros((1000, 128*128))
for i in range(1000):
    image1 = cv2.imread("./data/"+ str(i) +".png" , 2)
    image_save.append(image1)
    vector_image = []
    for j in range(128):
        vector_image.extend(image1[j])
    for j in range(128*128):
        matrix_image[i][j] = vector_image[j]
# chiếu 1000 ảnh sang không gian pca
matrix_image_pca = matrix_image.dot(pca)

#load ảnh cần match
image_path = input('nhập image path: ')
image_value = cv2.imread(image_path, 2)
vector_image_value = np.zeros((1,128*128))
_vector_image_value = []
for i in range(128):
    _vector_image_value.extend(image_value[i])
for i in range(128*128):
    vector_image_value[0][i] = _vector_image_value[i]
#chiếu ảnh sang không gian pca
vector_image_value_pca = vector_image_value.dot(pca)
#tính và sắp xếp (id) tăng dần khoảng cách của ảnh cần match với 1000 ảnh dữ liệu
check_length = []
for i in range(len(matrix_image_pca)):
    S = 0
    for j in range(len(vector_image_value_pca)):
        S += math.pow(vector_image_value_pca[0][j]-matrix_image_pca[i][j],2)
    S = math.sqrt(S)
    check_length.append(S)
def check_sort(elem):
    return check_length[elem]
id_image = []
for i in range(1000):
    id_image.append(i)
id_image.sort(key=check_sort)
# print(id_image)
#lấy ra 5 ảnh gần nhất với ảnh cần match
for i in range(5):
    cv2.imwrite("image"+str(i+1)+".png" ,image_save[id_image[i]])
