import matplotlib.pyplot as plt
import numpy as np 
from sklearn import tree
from sklearn.model_selection import train_test_split

def load_data_set(path, col):
    f = open(path, 'r')
    start_rp = 1
    all_data = f.read()
    lines = all_data.split('\n')
    x_ = []
    y = []
    print("========== loading data from ",path,"============")
    for i in range(1,len(lines)):
        if(len(lines[i]) > 0):
            row_array = lines[i].split(',')
            y.append(row_array[0])
            arr = []
            for j in range(start_rp, col):
                arr.append(row_array[j])
            x_.append(arr)
    print("=========== convert string data to int==========")
    x = [[0 for j in range(col - start_rp)] for i in range(len(x_))]
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
    print("=======DONE===========")

    return x,y
    
def process():
    # list_data, list_target = pretreatment("mushrooms.csv")
    list_data, list_target = load_data_set("mushrooms.csv", 23)
    x_train, x_test, y_train, y_test = train_test_split(list_data, list_target, test_size = 0.3)
    clf = tree.DecisionTreeClassifier()
    clf.fit(x_train, y_train)
    predic = clf.predict(x_test)
    tree.plot_tree(clf)
    print ( "Độ chính xác: ",100*sum(predic==y_test)/float(len(y_test)),"%")

process()

