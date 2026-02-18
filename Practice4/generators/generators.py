# Task 1: Generator for squares up to N
def gen_squares(N):
    for i in range(N):
        yield i ** 2

print("Squares:")
for x in gen_squares(5):
    print(x, end=" ")
print("\n")

# Task 2: Generator for even numbers
def gen_even(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

print("Even numbers:")
# Use * to unpack the generator and print with comma separator
print(*gen_even(10), sep=",")

# Task 3: Numbers divisible by 3 and 4
def div_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

print("\nDivisible by 3 and 4:")
for x in div_by_3_and_4(30):
    print(x, end=" ")
print("\n")

# Task 4: Generator for squares from a to b
def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2

print("Squares from 3 to 7:")
for x in squares(3, 7):
    print(x, end=" ")
print("\n")

# Task 5: Countdown generator
def countdown(n):
    while n >= 0:
        yield n
        n -= 1

print("Countdown:")
for x in countdown(5):
    print(x, end=" ")
print()