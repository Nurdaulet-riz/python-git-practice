import os
import subprocess
os.makedirs("folder/folder1/inner", exist_ok = True)
print("Nested directories created.")

code = """from datetime import datetime
now = datetime.now()
without = now.replace(microsecond = 0)
print(without)"""
with open("folder/folder1/inner/new_file.py", "w") as f:
    f.write(code)

with open("folder/folder1/check.txt", "w") as f:
    f.write("Move files from folder1 to folder")

    
items = os.listdir("folder/folder1/inner")
("content of inner:")
for item in items:
    print(item)

subprocess.run(["python3", "folder/folder1/inner/new_file.py"])


folder = "folder/folder1/inner"
for file in os.listdir(folder):
    if file.endswith(".py"):
        print(file)