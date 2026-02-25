#1
def squares(n):
    for i in range(1, n+1):
        yield i*i
    
n = int(input())
for i in squares(n):
    print(i)

#2
def even_numbers(n):
    for i in range(0, n+1, 2):
        yield str(i)

n = int(input())
first = True
for i in even_numbers(n):
    if not first:
        print(",", end = "")
    print(i, end = "")
    first = False

#3
def divtf(n):
    for i in range(0,n+1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input())
first = True
for i in divtf(n):
    if not first:
        print(",", end = "")
    print(i, end = "")
    first = False

#4
def squares(a,b):
    for i in range(a, b+1):
        yield i*i
    

a, b = map(int,input().split())
for i in squares(a, b):
    print(i)

#5
def pri(n):
    while n >= 0:
        yield n
        n -= 1
    
n = int(input())
first = True
for i in pri(n):
    if not first:
        print(",", end = "")
    print(i, end = "")
    first = False