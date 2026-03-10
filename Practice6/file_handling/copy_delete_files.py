import os
import shutil
shutil.copy("file1.txt", "new_file1.txt")
print("file copied!")

copy = "new_file1.txt"
if os.path.exists(copy):
    os.remove(copy)
    print(f"{copy} has been deleted.")
else:
    print(f"{copy} does not exist")