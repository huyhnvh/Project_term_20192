import numpy as np 
from fractions import Fraction as F 
import sys
# from decimal import Decimal

def pivot(a, p, q):
    (r, c) = a.shape
    for i in range (r):
        for j in range(c):
            if(i != p and j != q):
                a[i][j] -= (a[p][j]*a[i][q]/a[p][q])
    for i in range(r):
        if ( i != p):
            a[i][q] = F(0,1)
    for i in range(c):
        if(i != q):
            a[p][i] /= a[p][q]
    a[p][q] = F(1)
    return a 

# lấy nghiệm từ bảng đơn hình
def value_x(a):
    (r, c) = a.shape
    c_A = c - 1
    r_A = r - 1
    x = np.array([F(0,1) for i in range(c_A)])
    init_matrix = np.array([[F(0,1) for i in range(r_A)] for j in range(r_A+1)])
    for i in range(r_A):
        init_matrix[i][i] = F(1)
    for i in range(r_A):
        for j in range(c_A):
            if(list(a[:,j]) == list(init_matrix[:,i])):
                x[j] = a[i][c_A]
                break
    return x 

#simplex phase 1
def simplex1(a):
    (r, c) = a.shape
    while(True):
        #tìm pivot cho pha 1 , min âm -> cột, min dương tỷ số -> hàng
        p = 0
        q = 0
        check = True
        for i in range(c-1):
            if(a[r-1][i] < 0 and a[r-1][i] <= a[r-1][q]):
                q = i 
                check = False
        if (check):
            break 
        for i in range(r-2):
            if(a[i][q] > 0):
                p = i
                break 
        for i in range(p+1, r-2):
            if(a[i][q]> 0):
                if(a[i][c-1]/a[i][q] < a[p][c-1]/a[p][q]):
                    p = i 
        # gọi pivot cập nhật bảng
        a = pivot(a, p, q)
    return a

#simplex phase 2
def simplex2(a):
    (r, c) = a.shape
    while(True):
        # tìm pivot cho pha 2, max dương -> cột, min dương -> hàng
        p = 0
        q = 0
        check = True
        for i in range(c-1):
            if(a[r-1][i] > 0 and a[r-1][i] >= a[r-1][q]):
                q = i 
                check = False
        if (check):
            break 
        for i in range(r-1):
            if(a[i][q] > 0):
                p = i
                break 
        for i in range(p+1, r-1):
            if(a[i][q]> 0):
                if(a[i][c-1]/a[i][q] < a[p][c-1]/a[p][q]):
                    p = i
        # gọi pivot cập nhật bảng
        a = pivot(a,p,q)
    return a

def creat_table1(A,b,c, sum_column_insert, id_insert):
    (r_A, c_A) = A.shape
    if(sum_column_insert>0):
        # nếu như có biến giả được thêm vào:
        a = np.array([[F(0,1) for i in range(c_A+1+sum_column_insert)] for j in range(r_A+2)])
    else :
        # nếu không có biến giả
        a = np.array([[F(0,1) for i in range(c_A+1+sum_column_insert)] for j in range(r_A+1)])
    # khởi tạo hàm mục tiêu minimize sum(biến giả)
    for i in range(c_A, c_A+sum_column_insert):
        a[r_A+1][i] = F(1)
    # khởi tạo vế phải
    for i in range(r_A):
        for j in range(c_A):
            a[i][j] = A[i][j]
        a[i][c_A+sum_column_insert] = b[i]
    # hàm mục tiêu tương đương ( vì lúc này cột cơ sở đang ở biến giả nên phải biến đổi để hàm mục tiêu khác biến giả)
    v = c_A
    for i in range(r_A):
        if(id_insert[i] > 0):
            a[i][v] = F(1)
            v += 1
            a[r_A+1] -= a[i]
    # giữ nguyên hàm mục tiêu ban đầu
    for j in range(c_A):
        a[r_A][j] =c[j]
    return a

#tạo bảng đơn hình cho phase 2
def create_table2(a,c, sum_column_insert):
    (r_a, c_a) = a.shape
    # nếu có biến giả thì phải xoá hàm mục tiêu ở bảng đơn hình 1 :
    if(sum_column_insert>0):
        a = np.delete(a,r_a-1,0)
    (r_a, c_a) = a.shape
    # kiểm tra biến cơ sở có biến giả hay không
    base_line_virtual = []
    for j in range(c_a-1-sum_column_insert, c_a -1):
        count0 = 0
        count1 = 0
        num_base = 0
        for i in range(r_a - 1):
            if(a[i][j] == F(0,1)):
                count0 += 1
            if(a[i][j] == F(1)):
                count1 += 1
                num_base = i
        if( count0 == r_a-1 and count1 == 1):
            base_line_virtual.append(num_base)
    # nếu có biến giả cơ sở : kiểm tra nghiệm giả nếu khác 0 => bài toán vô nghiệm
    if(len(base_line_virtual) != 0):
        for i in base_line_virtual:
            if(a[i][c_a-1] != F(0,1) ):
                print("don't have solve!")
                sys.exit()
        # ngược lại kiểm tra trên dòng cơ sở của biến giả xem hệ số của biến thực có = 0 ?
        base_line_virtual.sort(reverse=True)
        for i in base_line_virtual:
            for j in range(c_a-1-sum_column_insert):
                # nếu  khác 0 phải pivot để thế cơ sở giả bằng cơ sở khác
                if(a[i][j] != F(0,1)):
                    a = pivot(a,i,j)
                    # gọi lại hàm để xét lại từ đầu
                    return create_table2(a,c, sum_column_insert)
            # nếu hệ số biến thực đều bằng 0 thì xoá dòng cơ sở giả
            a = np.delete(a, i, 0)
    # xoá cột biến giả
    for i in range(sum_column_insert):
        a = np.delete(a,c_a-1-sum_column_insert,1)
    return a 

# A = b
# maximize c
def simplex_2_phase(A, b, c ):
    print("========= start simplex 2 phase ========")
    (r_A, c_A) = A.shape
    # tìm các biến phụ cần thêm
    sum_column_insert = r_A #số biến phụ cần thêm
    id_insert = np.array([int(1) for i in range(r_A)]) # vị trí thêm ( = 1 thì cần thêm )
    for j in range(c_A):
        count0 = 0
        count1 = 0
        t = r_A + 1 
        for i in range(r_A):
            if(A[i][j] == F(0,1)):
                count0 += 1
            if(A[i][j] == F(1)):
                count1 += 1
                t = i 
        if (c[j] == F(0,1) ):
            count0 += 1
        if(count0 == r_A and count1 == 1):
            if(id_insert[t] != 0):
                sum_column_insert -= 1
                id_insert[t] = 0
    # khởi tạo bảng đơn hình cho phase 1
    a = creat_table1(A,b,c,sum_column_insert,id_insert)
    print_solution(a, [F(0)])
    #chạy phase 1
    if(sum_column_insert != 0):
        print("======run phase 1=======")
        a = simplex1(a)
    print_solution(a, [F(0)])
    a = create_table2(a, c,sum_column_insert)
    #chạy phase 2
    print("=========run phase 2==========")
    a = simplex2(a)
    #trích rút nghiệm 
    x = value_x(a)
    print_solution(a, x)
    # print(x)
    return x , a

def dual_simplex(a):
    print("==========run dual===========")
    (r_a, c_a) = a.shape
    
    while(True):
        # tìm pivot tìm max dương vế phải => hàng, min âm (hệ số mục tiêu /hệ số các biến trên hàng) 
        p = 0
        for i in range(1,r_a-1):
            if(a[i][c_a-1] < a[p][c_a-1]):
                p = i 
        if(a[p][c_a-1] >= 0):
            break
        q = 0 
        check = True
        for i in range(c_a-1):
            if(a[p][i] < 0):
                q = i 
                check = False
                break
        if(check ):
            print("don't have solution!")
            sys.exit()
        for i in range(q+1, c_a -1 ):
            if(a[p][i] < 0 and a[r_a-1][i]>=0 ):
                if(a[r_a-1][i]/a[p][i] > a[r_a-1][q]/a[p][q]):
                    q = i 
        # gọi pivot cập nhật bảng
        a = pivot(a,p,q)
    x = value_x(a)
    return x,a 
        
def print_solution(a, x):
    (r, c) = a.shape
    s = ''
    s1 = ''
    for i in range(r):
        s += '\n'
        for j in range(c):
            s1 = str(a[i][j])
            s += s1
            if(j != c-1):
                for k in range(6-len(s1)):
                    s += ' '
    print('===== array a ====\n', s)
    if(len(x) > 0):
        s = '\n'
        for i in range(len(x)):
            s1 =''
            if(x[i].denominator == 1):
                s1 += str(x[i].numerator)
            else:
                s1 += str(x[i].numerator)+'/'+str(x[i].denominator)
            s += s1
            k = len(s1)
            for j in range(6 - k):
                s += ' '
            
    print('\n\n===== array x ==== \n', s)

def gomory_cut(A,b,c, integer_var):
    # chạy đơn hình hai pha 
    x,a =  simplex_2_phase(A, b, c)
    print_solution(a,x)
    t=0
    while(True):
        t += 1
        (r_a, c_a) = a.shape
        # thêm ràng buộc
        id_constraint_add = []
        for i in integer_var:
            if(x[i].denominator != 1):
                id_constraint_add.append(i)
                break
        num_constraint_add = len(id_constraint_add)
        if(num_constraint_add == 0):
            break
        # bảng đơn hình mới
        b = np.array([[F(0,1) for i in range(c_a + num_constraint_add)] for j in range(r_a + num_constraint_add)])
        r_b = r_a + num_constraint_add
        c_b = c_a + num_constraint_add
        for i in range(r_a-1):
            b[i][c_b-1] = a[i][c_a-1]
            for j in range(c_a-1):
                b[i][j] = a[i][j]
        b[r_b-1][c_b-1] = -a[r_a-1][c_a-1]
        for j in range(c_a-1):
            b[r_b-1][j] = -a[r_a-1][j]
        for k in range(num_constraint_add):
            i = id_constraint_add[k]
            for j in range(c_b):
                if(b[i][j] < F(0,1)):
                    b[r_a-1+k][j] = -(b[i][j]-F(int(b[i][j]) - 1))
                else:
                    b[r_a-1+k][j] = -(b[i][j]-F(int(b[i][j])))
        for i in range(num_constraint_add):
            b[r_a-1+i][c_a-1+i] = F(1)
        print_solution(b,x)
        # chạy dual simplex
        x,a = dual_simplex(b)
    return x,a 

def solve(input_data):
    line = input_data.split('\n')
    integer_var = []
    c = []
    for i in line[0].split(' '):
        if(len(i) > 0):
            integer_var.append(int(i))
    for i in line[1].split(' '):
        if(len(i) > 0):
            val = i.split('/')
            if(len(val) == 1):
                c.append(F(int(val[0])))
            else:
                c.append(F(int(val[0]), int(val[1])))
    A = []
    b = []
    l = len(c)
    for i in range(2, len(line)):
        check_count = 0
        A0 = []
        for j in line[i].split(' '):
            if(len(j) > 0):
                check_count += 1
                val = j.split('/')
                val_F = 0
                if(len(val) == 1):
                    val_F = F(int(val[0]))
                else:
                    val_F = F(int(val[0]), int(val[1]))
                if(check_count <= l):
                    A0.append(val_F)
                else:
                    A.append(A0)
                    b.append(val_F)
    A = np.array(A)
    b = np.array(b)
    c = np.array(c)
    x,a = gomory_cut(A,b,c,integer_var)
    print_solution(a,x)

if __name__ == '__main__':
    import sys
    if(len(sys.argv) > 1):
        file_name = sys.argv[1].strip()
        with open(file_name, 'r') as file_open:
            input_data = file_open.read()
        solve(input_data)
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python gomory.py ./data/g_5_0)')    
