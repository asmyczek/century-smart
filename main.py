from sensor.main import start_service
import time, gc, ntptime


time.sleep_ms(100)
gc.collect()

time.sleep_ms(500)
ntptime.settime()

start_service()

