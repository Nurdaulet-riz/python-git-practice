from datetime import datetime
now = datetime.now()
without = now.replace(microsecond = 0)
print(without)