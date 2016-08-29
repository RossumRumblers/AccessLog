from time import strftime, sleep
from datetime import datetime, timedelta

lastlog = datetime.now()
#strftime("%Y-%m-%d %H:%M:%S")
sleep(5)
delta = datetime.now() - lastlog

print(delta.seconds)
