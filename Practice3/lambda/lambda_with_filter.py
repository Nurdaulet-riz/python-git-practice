#Filter out even numbers from a list:
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
odd_numbers = list(filter(lambda x: x % 2 != 0, numbers))
print(odd_numbers)

#Filter out odd numbers from a list:
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(even_numbers)

#Filter strings that start with a capital letter:
names = ["Alice", "bob", "Charlie", "david"]
capital_names = list(filter(lambda x: x[0].isupper(), names))
print(capital_names)

#Filter emails that contain “@gmail”:
emails = ["a@gmail.com", "b@yahoo.com", "c@gmail.com"]
gmail_only = list(filter(lambda e: "@gmail" in e, emails))
print(gmail_only)
