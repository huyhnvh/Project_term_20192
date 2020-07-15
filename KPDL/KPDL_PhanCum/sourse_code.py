from sklearn.cluster import KMeans
import numpy as np 
from sklearn.metrics import davies_bouldin_score

# load data from path, number of data set(1-4) ?, how much column of data set?
def load_data_set(noSet,path, col):
    print("==============Loading=========")
    f = open(path, 'r')
    start_rp = 0
    if(noSet == 2):
        start_rp = 1
    all_data = f.read()
    lines = all_data.split('\n')
    x_ = []
    for i in range(1,len(lines)):
        if(len(lines[i]) > 0):
            row_array = lines[i].split(',')
            arr = []
            for j in range(start_rp, col):
                # print(i,"  ",j)
                arr.append(row_array[j])
            x_.append(arr)
    x = [[0 for j in range(col - start_rp)] for i in range(len(x_))]
    print("=========Convert data to int===============")
    for j in range(col-start_rp):
        t = 0
        for i in range(len(x_)):
            check = True 
            for k in range(i):
                if(x_[k][j] == x_[i][j]):
                    x[i][j] = x[k][j]
                    check = False
                    break
            if(check):
                x[i][j] = t 
                t += 1
        
    x = np.array(x)
    print(np.shape(x))
    print("==============done==============")
    return x

def kmean_run():
    # x = load_data_set(1, "kaggle_Interests_group.csv",219)
    # x = load_data_set(2,"Turkey Mobil Data Usage Plain Data V1.csv", 59)
    x = load_data_set(3, "OnlineRetail.csv", 8)
    # x = load_data_set(4, "wine-clustering.csv",13)
    y = [0 for i in range(len(x))]
    score_min = 1<<15
    print("========training==========")
    for i in range(2, 11):
        kmean = KMeans(n_clusters=i, random_state= 1).fit(x)
        label = kmean.labels_
        score = davies_bouldin_score(x, label)
        if(score_min > score):
            score_min = score
            y = label
    print("========== output file result.csv===========")
    f = open("result.csv", 'w')
    s = 'Min davies bouldin score = '+str(score_min)+'\nLabels: \n'
    for i in range(len(y)):
        s += str(y[i])+'\n'
    f.write(s)
    return y

kmean_run()