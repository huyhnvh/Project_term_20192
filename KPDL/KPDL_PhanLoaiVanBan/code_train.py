from sklearn.naive_bayes import MultinomialNB
import numpy as np 

def clean_word(w):
    w_cleaned =""
    if(w != ""):
        for i in range(len(w)):
            if(w[i]>="a" and w[i]<="z"):
                w_cleaned += w[i]
    return w_cleaned

def check_stop_word(w, list_sw):
    try:
        list_sw.index(w)
    except ValueError:
        return True
    return False

def process():
    filer = open("bbc-text.csv","r")
    all_paragraphs = filer.read()
    list_paragraph  = all_paragraphs.split("\n")
    category =[]
    dictionary=[]
    filer1 = open("stop-word.csv", "r")
    sw = filer1.read()
    list_sw = sw.split("\n")
    file_w1 = open("tech.csv", "w")
    file_w2 = open("sport.csv", "w")
    file_w3 = open("entertainment.csv", "w")
    file_w4 = open("business.csv", "w")
    file_w5 = open("politics.csv", "w")
    for p in list_paragraph:
        if(p != ""):
            l = p.split(",")
            category.append(l[0])
            words = l[1].split(" ")
            for i in range(len(words)):
                word = words[i]
                word_cl = clean_word(word)
                if(word_cl != ""): 
                    if(check_stop_word(word_cl,list_sw)):
                        if (l[0] == "tech"):
                            file_w1.write(word_cl + ",")
                        if(l[0] == "sport"):
                            file_w2.write(word_cl + ",")
                        if(l[0] == "business"):
                            file_w4.write(word_cl + ",")
                        if(l[0] == "entertainment") :
                            file_w3.write(word_cl + ",")
                        if(l[0]=="politics"):
                            file_w5.write(word_cl + ",")
                        try:
                            dictionary.index(word_cl)
                        except ValueError:
                            dictionary.append(word_cl)
            if (l[0] == "tech"):
                file_w1.write("\n")
            if(l[0] == "sport"):
                file_w2.write("\n")
            if(l[0] == "business"):
                file_w4.write("\n")
            if(l[0] == "entertainment") :
                file_w3.write("\n")
            if(l[0]=="politics"):
                file_w5.write("\n")

    filew = open("dictionary.csv", "w")
    print(category)
    for w in dictionary:
        filew.write(w + "," )

def load_data_train(size_data):
    filer_tech = open("tech.csv", "r")
    filer_sport = open("sport.csv", "r")
    filer_business = open("business.csv", "r")
    filer_entertainment = open("entertainment.csv", "r")
    filer_politics = open("politics.csv","r")
    filew = open("data_train_"+str(size_data)+"_2.csv", "w")
    filew2 = open("data_train_"+str(size_data)+"_5.csv", "w")
    for i in range(size_data):
        line = filer_tech.readline()
        filew.write("tech ")
        filew.write(line)
        filew2.write("tech ")
        filew2.write(line)
    for i in range(size_data):
        line = filer_sport.readline()
        filew2.write("sport ")
        filew2.write(line)
        if(i<size_data/4):
            filew.write("no-tech ")
            filew.write(line)
    for i in range(size_data):
        line = filer_entertainment.readline()
        filew2.write("entertainment ")
        filew2.write(line)
        if(i<size_data/4):
            filew.write("no-tech ")
            filew.write(line)
    for i in range(size_data):
        line = filer_business.readline()
        filew2.write("business ")
        filew2.write(line)
        if(i<size_data/4):
            filew.write("no-tech ")
            filew.write(line)
    for i in range(size_data):
        line = filer_politics.readline()
        filew2.write("politics ")
        filew2.write(line)
        if(i<size_data/4):
            filew.write("no-tech ")
            filew.write(line)
def load_data_test(filename):
    filer = open(filename, "r")
    filew = open("data_test1.csv", "w")
    all_data = filer.read()
    lines = all_data.split("\n")
    filer1 = open("stop-word.csv", "r")
    sw = filer1.read()
    list_sw = sw.split("\n")
    print(len(lines))
    for line in lines:
        if(line != ""):
            l = line.split(",")
            filew.write(l[0]+",")
            w = l[1].split(" ")
            for i in range(len(w)):
                word_cl = clean_word(w[i])
                if(word_cl != "" and check_stop_word(word_cl,list_sw)): 
                    filew.write(word_cl)
                    if(i < len(w)-1):
                        filew.write(" ")
                if(i == len(w)-1):
                    filew.write("\n")
                    
        else: 
            print(line)

load_data_train(200)