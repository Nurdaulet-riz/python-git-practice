class Flyer:
    def move(self):
        return "Flying"


class Swimmer:
    def move(self):
        return "Swimming"


class Duck(Flyer, Swimmer):  # multiple inheritance
    pass


duck = Duck()
print(duck.move())
