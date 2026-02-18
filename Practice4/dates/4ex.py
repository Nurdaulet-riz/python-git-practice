from datetime import datetime
date1 = datetime.now()
date2 = datetime(2026, 2, 1)
difference = date1 - date2
seconds = difference.total_seconds()
print(seconds)