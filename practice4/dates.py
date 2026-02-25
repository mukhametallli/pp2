#1
from datetime import datetime, timedelta

now = datetime.now()
newd = now - timedelta(days = 5)
print(newd)

#2
from datetime import datetime, timedelta
today = datetime.now()
yesterday = today - timedelta(days = 1)
tomorrow = today + timedelta(days = 1)
print("Yesterday:", yesterday)
print("Today:", today)
print("Tomorrow:", tomorrow)

#3
from datetime import datetime
now = datetime.now()
without_microseconds = now.replace(microsecond = 0)
print(without_microseconds)

#4
from datetime import datetime
date1 = datetime(2008, 4, 10, 17, 0, 0)
date2 = datetime(2026, 2, 22, 13, 46, 0)

difference = date2 - date1
print("Difference in seconds:", difference.total_seconds())