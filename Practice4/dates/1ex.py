from datetime import datetime, timedelta
current_date = datetime.now()
new_date = current_date - timedelta(days = 5)
print("current_date:", current_date)
print("date minus 5 days", new_date)
