#A function with one argument:
def my_function(fname):
  print(fname + " Refsnes")

my_function("Emil")
my_function("Tobias")
my_function("Linus")

#A function with two argument:
def my_function(fname, lname):
  print(fname + " " + lname)

my_function("Emil", "Refsnes")

#default values to parameters:
def my_function(name = "friend"):
  print("Hello", name)

my_function("Emil")
my_function("Tobias")
my_function()
my_function("Linus")

#arguments with the key = value syntax:
def my_function(animal, name):
  print("I have a", animal)
  print("My", animal + "'s name is", name)

my_function(animal = "dog", name = "Buddy")

#Sending a list as an argument:
def my_function(fruits):
  for fruit in fruits:
    print(fruit)

my_fruits = ["apple", "banana", "cherry"]
my_function(my_fruits)

#Sending a dictionary as an argument:
def my_function(person):
  print("Name:", person["name"])
  print("Age:", person["age"])

my_person = {"name": "Emil", "age": 25}
my_function(my_person)

#Positional-Only Arguments:
def my_function(name, /):#To specify positional-only arguments, add , / after the arguments
  print("Hello", name)

my_function("Emil")

#Keyword-Only Arguments:
def my_function(*, name):#To specify that a function can have only keyword arguments, add *, before the arguments
  print("Hello", name)

my_function(name = "Emil")

#Combining Positional-Only and Keyword-Only:
def my_function(a, b, /, *, c, d):
  return a + b + c + d

result = my_function(5, 10, c = 15, d = 20)
print(result)
