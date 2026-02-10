#Sort a list of tuples by the second element:
students = [("Emil", 25), ("Tobias", 22), ("Linus", 28)]
sorted_students = sorted(students, key=lambda x: x[1])
print(sorted_students)

#Sort strings by length:
words = ["apple", "pie", "banana", "cherry"]
sorted_words = sorted(words, key=lambda x: len(x))
print(sorted_words)

#Sort numbers by distance from 10:
nums = [3, 14, 7, 20]
sorted_nums = sorted(nums, key=lambda x: abs(x - 10))
print(sorted_nums)

#reverse sorting
nums = [5, 2, 9, 1]
sorted_nums = sorted(nums, key=lambda x: x, reverse=True)
print(sorted_nums)
