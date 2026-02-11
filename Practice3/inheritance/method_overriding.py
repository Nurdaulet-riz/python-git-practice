class Animal:
    def speak(self):
        return "Some sound"


class Dog(Animal):
    def speak(self):  # overriding parent method
        parent_sound = super().speak()  # call parent method (optional)
        return parent_sound + " -> Woof!"


d = Dog()
print(d.speak())
