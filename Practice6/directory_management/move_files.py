import shutil
import os

#shutil.copy("folder/folder1/inner/check.txt", "folder/check.txt")
#print("file copied successfully")

#os.remove("folder/check.txt")

shutil.move("folder/check.txt", "folder/folder1/check.txt")
print("file moved successfully")