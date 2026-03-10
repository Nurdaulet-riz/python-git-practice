with open("file1.txt", "r") as f:
    info = f.read()
print(info)

with open("file1.txt", "a") as f:
    f.write("this is an appended line.\n")

with open("file1.txt", "r") as f:
    info = f.read()
print(info)