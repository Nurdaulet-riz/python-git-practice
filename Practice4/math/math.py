import math

# Task 1: Convert degree to radian
degree = 15
radian = degree * (math.pi / 180)
print(f"Degree: {degree}, Radian: {radian:.6f}")

# Task 2: Calculate Area of a Trapezoid
# Formula: ((base1 + base2) / 2) * height
height = 5
base1 = 5
base2 = 6
area_trap = ((base1 + base2) / 2) * height
print(f"Trapezoid Area: {area_trap}")

# Task 3: Calculate Area of Regular Polygon
# Formula: (n * s^2) / (4 * tan(pi/n))
n_sides = 4
length = 25
area_poly = (n_sides * length**2) / (4 * math.tan(math.pi / n_sides))
print(f"Polygon Area: {int(area_poly)}")

# Task 4: Calculate Area of a Parallelogram
# Formula: base * height
base = 5
height = 6
area_para = base * height
print(f"Parallelogram Area: {float(area_para)}")