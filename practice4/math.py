#1
import math
degree = float(input())
radian = degree * math.pi / 180
print(f"{radian:.6f}")

#2
height = int(input())
a = float(input())
b = float(input())

area = (a+b)/2 * height
print(area)

#3
import math
ns = int(input())
length = int(input())

area = int((ns * pow(length, 2))/ (4 * math.tan(math.pi / ns)))
print(area)

#4
lenght = float(input())
height = float(input())

area = lenght * height
print(area)