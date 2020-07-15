from cv2 import cv2
import numpy as np 
import os

_bool = True
count_image = 0
while(1):
    for i in range(50):
        if(count_image == 1000):
                    break
        for j in range(100):
            path = "./images/"+str(i)+"/"+str(j)+".png"
            if(os.path.isfile(path)):
                count_image += 1
                image = cv2.imread(path,2)
                image = cv2.resize(image,(128,128))
                cv2.imwrite(str(count_image)+".png",image)
                if(count_image == 1000):
                    break
            else:
                j=100
        
    break

