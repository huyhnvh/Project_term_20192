from sklearn.naive_bayes import MultinomialNB
import numpy as np 

def load_data(dictionary_file,train_file, test_file):
    print("=========load dictionary=======")
    # tải bộ dữ liệu từ điển
    filer = open(dictionary_file,"r")
    load_data_dictionary = filer.read()
    dictionary = load_data_dictionary.split(",")
    # tải bộ data train
    print("==========load train data========")
    filer = open(train_file, "r")
    load_data_train  = filer.read()
    list_paragraph = load_data_train.split("\n")
    matrix_data_train = np.zeros((len(list_paragraph),len(dictionary)))
    category_train =[]
    for i in range(len(list_paragraph)):
        l = list_paragraph[i].split(" ")
        category_train.append(l[0])
        list_word = l[1].split(",")
        for j in range(len(dictionary)):
            matrix_data_train[i][j] = list_word.count(dictionary[j])
    # tải bộ data test
    print("=============load test data=============")
    filer2 = open(test_file,"r")
    load_data_test = filer2.read()
    lines = load_data_test.split("\n")
    matrix_data_test = np.zeros((len(lines),len(dictionary)))
    category_real =[]
    for i in range(len(lines)):
        l = lines[i].split(",")
        category_real.append(l[0])
        list_word = l[1].split(" ")
        for j in range(len(dictionary)):
            matrix_data_test[i][j] = list_word.count(dictionary[j])
    category_train_nparray = np.array(category_train)
    print("---------------complete-------------")
    return matrix_data_train, category_train_nparray, matrix_data_test, category_real


def test_func(dictionary_file,train_file, test_file, sum_class):
    x_train, y_train, x_test, y_test = load_data(dictionary_file,train_file, test_file )
    # naive-bayes model
    print("============training============")
    MNB = MultinomialNB()
    # training
    MNB.fit(x_train, y_train)
    # tính predict
    print("======= test result with new data ===========")
    category_geuss = MNB.predict(x_test)
    percent_true = 0
    for i in range(len(y_test)):
        if(sum_class != 2):
            if(y_test[i] == category_geuss[i]):
                percent_true += 1
        else:
            if(y_test[i] == category_geuss[i]):
                percent_true += 1
            if(y_test[i] != "tech" and category_geuss[i] == "no-tech"):
                percent_true += 1
    print("DONE!")
    # tính độ chính xác
    percent_true /= len(y_test)
    print('độ chính xác : ', 100*percent_true,'%')
test_func("dictionary.csv","data_train_200_5.csv","data_test1.csv", 5)


