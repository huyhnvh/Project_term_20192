import pandas as pd 
import sklearn
from  sklearn.model_selection import train_test_split
import numpy as np

filer = open('data_crawled.csv', 'r', encoding="utf8")
data = filer.read()
filew = open('data_crawl.csv', 'w', encoding="utf8")
lines = data.split('\n')
filew.write(lines[0] + '\n')
for i in range(5):
    for j in range(1,501) :
        filew.write(lines[i*1500 + j] + '\n')
