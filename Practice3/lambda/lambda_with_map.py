#Double all numbers in a list:
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)

#square of numbers:
numbers = [4, 5, 32, 3, 9]
square = list(map(lambda x: x ** 2, numbers))
print(square)

#Add number:
numbers = [4, 5, 6, 7, 8]
add = list(map(lambda x : x + 15, numbers))
print(add)

#Convert list of strings to integers:
numbers_str = ["1", "2", "3", "4", "5"]

numbers_int = list(map(lambda x: int(x), numbers_str))

print(numbers_int)
