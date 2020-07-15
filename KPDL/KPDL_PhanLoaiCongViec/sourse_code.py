
import numpy as np 
from sklearn import tree
from sklearn.model_selection import train_test_split

def load_data_set(path, col):
    f = open(path, 'r',encoding="utf8")
    start_rp = 1
    all_data = f.read()
    lines = all_data.split('\n')
    x_ = []
    y = []
    print("========== loading data from ",path,"============")
    for i in range(1,len(lines)):
        if(len(lines[i]) > 0):
            row_array = lines[i].split('"')
            arr = []
            mini_array = row_array[0].split(",")
            arr.append(mini_array[1])
            for j in range(1,len(row_array)-1):
                if(j%2 == 1):
                    arr.append(row_array[j])
                else:
                    mini_array = row_array[j].split(",")
                    for k in range(1,len(mini_array)-1):
                        arr.append(mini_array[k])
            mini_array = row_array[len(row_array)-1].split(",")
            for j in range(1,len(mini_array)-1):
                arr.append(mini_array[j])
            if(len(arr) == 16):
                y.append(mini_array[len(mini_array)-1])
                x_.append(arr)
    print("=========== convert string data to int==========")
    x = [[0 for j in range(col - 1 - start_rp)] for i in range(len(x_))]
    for j in range(col-1-start_rp):
        print(j)
        t = 0 
        for i in range(len(x_)):
            # print("i,j ", i," ",j)
            check = True
            for k in range(i):
                if(x_[k][j] == x_[i][j]):
                    x[i][j] = x[k][j]
                    check = False
                    break
            if(check):
                x[i][j] = t
                t += 1
    print("===============write data number==============")
    filew = open("data_number.csv", "w")
    for i in range(len(x)):
        for j in range(col-2):
            filew.write(str(x[i][j])+',')
        filew.write(str(y[i])+'\n')
    x = np.array(x)
    print("=======DONE===========")

    return x,y
    
def process():
    # list_data, list_target = pretreatment("mushrooms.csv")
    list_data, list_target = load_data_set("fake_job_postings.csv", 18)
    print("================Training============")
    x_train, x_test, y_train, y_test = train_test_split(list_data, list_target, test_size = 0.3)
    clf = tree.DecisionTreeClassifier()
    clf.fit(x_train, y_train)
    predic = clf.predict(x_test)
    print ( "Độ chính xác: ", 100*sum(predic==y_test)/float(len(y_test)),"%")

process()

