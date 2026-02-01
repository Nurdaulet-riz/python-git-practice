#and
x = 5

print(x > 0 and x < 10)
#or
x = 5

print(x < 5 or x > 10)
#Reverse the result with not
x = 5

print(not(x > 3 and x < 10))

# is
x = ["apple", "banana"]
y = ["apple", "banana"]
z = x

print(x is z)
print(x is y)
print(x == y)

#is not
x = ["apple", "banana"]
y = ["apple", "banana"]

print(x is not y)
#Difference Between is and ==
x = [1, 2, 3]
y = [1, 2, 3]

print(x == y)
print(x is y)

#in
fruits = ["apple", "banana", "cherry"]

print("banana" in fruits)

#not in
fruits = ["apple", "banana", "cherry"]

print("pineapple" not in fruits)

#in strings
text = "Hello World"

print("H" in text)
print("hello" in text)
print("z" not in text)
