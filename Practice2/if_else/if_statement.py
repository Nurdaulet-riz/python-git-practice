thislist = ["apple", "banana", "cherry"]
if "apple" in thislist:
  print("Yes, 'apple' is in the fruits list")

number = 15
if number > 0:
  print("The number is positive")

#Using a boolean variable:
is_logged_in = True
if is_logged_in:
  print("Welcome back!")

#One-line if statement
a = 5
b = 2
if a > b: print("a is greater than b")

#nested if statements
x = 41

if x > 10:
  print("Above ten,")
  if x > 20:
    print("and also above 20!")

temperature = 25
is_sunny = True

if temperature > 20:
  if is_sunny:
    print("Perfect beach weather!")
