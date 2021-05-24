from machine import reset, Timer

class WatchDog:
    def __init__(self, timeout=60):
        self.timeout = timeout
        self.timer = Timer(0)
        self.init()

    def init(self):
        self.counter = 0
        self.timer.init(period=1000, callback=self.count, mode=Timer.PERIODIC)

    def count(self, t):
        self.counter += 1
        if self.counter >= self.timeout:
            print('Rebooting...')
            reset()

    def feed(self):
        self.counter = 0

    def deinit(self):
        self.timer.deinit()

WDT = WatchDog()
