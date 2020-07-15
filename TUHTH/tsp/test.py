a = range(5)
for i in range(5)[::-1]:
    print(a[i])
    if i == 4:
        i -= 1