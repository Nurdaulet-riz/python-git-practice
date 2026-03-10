input = list(map(int, input().split()))
x = list(map(lambda x : x ** 2, input))
print(x)

y = list(filter(lambda x : x % 2 == 0, input))
print(y)

from functools import reduce
total = reduce(lambda x, y : x + y, input)
print(total)

from functools import reduce
product = reduce(lambda x, y: x * y, input)
print(product)
