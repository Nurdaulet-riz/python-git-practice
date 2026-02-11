class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)


class Student(Person):  # Student inherits from Person
    pass


s1 = Student("John", "Doe")
s1.printname()   # inherited method
print(s1.firstname)  # inherited property

