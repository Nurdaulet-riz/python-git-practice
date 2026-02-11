#Create a class named Person, use the __init__() method to assign values for name and age:
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

p1 = Person("Emil", 36)

print(p1.name)
print(p1.age)

#set initial values when creating the object:
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

p1 = Person("Linus", 28)
p2 = Person("Maks", 18)
p3 = Person("Rishat", 17)
print(p1.name, end = ": ")
print(p1.age)
print(p2.name, end = ": ")
print(p2.age)
print(p3.name, end = ": ")
print(p3.age)

#Set a default value for the age parameter:
class Person:
  def __init__(self, name, age=18):
    self.name = name
    self.age = age

p1 = Person("Emil")
p2 = Person("Tobias", 25)

print(p1.name, p1.age)
print(p2.name, p2.age)

#Create a Person class with multiple parameters:
class Person:
  def __init__(self, name, age, city, country):
    self.name = name
    self.age = age
    self.city = city
    self.country = country

p1 = Person("Linus", 30, "Oslo", "Norway")

print(p1.name)
print(p1.age)
print(p1.city)
print(p1.country)

#Challenge: __init__ Method:
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def bark(self):
        print(self.name + " says Woof!")
# Create an object
d1 = Dog("Buddy", 3)
# Print the age
print(d1.age)
# Call the bark method
d1.bark()
