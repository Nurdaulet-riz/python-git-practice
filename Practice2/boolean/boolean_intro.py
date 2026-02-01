#Print a message based on whether the condition is True or False:
a = 200
b = 33

if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a")
#Evaluate a string and a number:
print(bool("Hello")) #True
print(bool(15)) #True
#Evaluate two variables:
x = "Hello"
y = 15

print(bool(x)) #True
print(bool(y)) #True

#The following will return False:
print(bool(False))
print(bool(None))
print(bool(0))
print(bool(""))
print(bool(()))
print(bool([]))
print(bool({}))

class myclass():
  def __len__(self):
    return 0

myobj = myclass()
print(bool(myobj))
#Print "YES!" if the function returns True, otherwise print "NO!":
def myFunction() :
  return True

if myFunction():
  print("YES!")
else:
  print("NO!")
#Check if an object is an integer or not:
x = "al"
print(isinstance(x, int)) #False
