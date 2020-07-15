from collections import namedtuple
from sys import maxsize
Item = namedtuple("Item", ["count", "st"])

def pretty_printing(L,input_data):
    paragraghs = input_data.split('/n')
    num_para = 0
    for paragraph in paragraghs:
        num_para = num_para +1
        print ("paragragh ",num_para , ":" )
        def printSolution(p, n): 
            k = 0
            if p[n] == 0: 
                k = 0
            else: 
                k = printSolution(p, p[n] - 1) + 1
            for i in range(p[n], n+1):
                if(i!=n):
                    print(items[i].st, end=" ")
                else:
                    print(items[i].st)
           #print('Line number ', k, ': From word no. ', p[n], 'to ', n) 
            return k 
        ws = paragraph.split(' ')
        items = []
        for w in ws :
            items.append(Item( len(w) , w ) )
        
        count_items = len(items)
        leng = [[-1 for i in range(count_items)] for i in range(count_items)]
        cost =[maxsize for i in range (count_items+1)]
        tick = [0 for i in range(count_items)]

        for i in  range(count_items):
            leng[i][i] = L - items[i].count
            for j in range(i+1, count_items):
                if ( items[j].count +1  <= leng[i][j-1]) :
                    leng[i][j] = leng[i][j-1] - ( items[j].count +1)
                    #print ("leng[", i , "][", j ,"] = ", leng[i][j])

        for i in range(count_items):
            for j in range(i, count_items):
                if(leng[i][j] >= 0):
                    leng[i][j] = leng[i][j] * leng[i][j]

        cost[0] = 0

        for j in range(1,count_items+1):
            for i in range(1,j+1):
                if(cost[i-1]>=0 and leng[i-1][j-1]>=0 and cost[i-1]+leng[i-1][j-1]< cost[j]):
                    cost[j] = cost[i-1] + leng[i-1][j-1]
                    tick[j-1]=i-1
        printSolution(tick,count_items-1)
        
        
                
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            l = input_data_file.readline()
            L = int(l)
            input_data = input_data_file.read()
        pretty_printing(L,input_data)
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

            