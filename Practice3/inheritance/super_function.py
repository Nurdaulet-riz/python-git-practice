class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)


class Student(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)   # call parent constructor
        self.graduationyear = year


s2 = Student("Alice", "Smith", 2027)
s2.printname()
print("Year:", s2.graduationyear)
