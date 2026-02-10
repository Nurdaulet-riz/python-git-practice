#A function that returns a value:
def get_greeting():
  return "Hello from a function"

message = get_greeting()
print(message)

#Using the return value directly:
def get_greeting():
  return "Hello from a function"

print(get_greeting())

#3
def my_function(x, y):
  return x + y

result = my_function(5, 3)
print(result)
#A function that returns a list:
def my_function():
  return ["apple", "banana", "cherry"]

fruits = my_function()
print(fruits[0])
print(fruits[1])
print(fruits[2])

#A function that returns a tuple:
def my_function():
  return (10, 20)

x, y = my_function()
print("x:", x)
print("y:", y)
