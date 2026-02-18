from datetime import datetime
now = datetime.now()
without = now.replace(microsecond = 0)
print("origin:", now)
print("without microseconds:", without)

time = datetime.now()
new_without = time.strftime("%Y-%m-%d %H:%M:%S")
print("NEW without microseconds:", new_without)