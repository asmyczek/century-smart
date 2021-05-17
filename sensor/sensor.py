from sensor.mqtt import CLIENT as mqtt
from machine import ADC, Pin, Timer, WDT
from micropython import schedule, alloc_emergency_exception_buf
from time import ticks_ms, ticks_diff
from uasyncio import sleep
from config import PIN_SENSOR, ALERT_INERTVAL_TIME, IDLE_INERTVAL_TIME

# alloc_emergency_exception_buf(100)

PIN_LIGHT = ADC(0)

GATE_STATUS_CLOSED = 'CLOSED'
GATE_STATUS_OPEN = 'OPEN'
GATE_STATUS_OPENING = 'OPENING'
GATE_STATUS_CLOSING = 'CLOSING'

GATE_ALERT_OK = 'OK'
GATE_ALERT_FLOODLIGHT_OVERRIDE = 'OVERRIDE'
GATE_ALERT_NO_MAIN_POWER = 'NO_MAIN'
GATE_ALERT_BATTERY_LOW = 'BATTERY_LOW'
GATE_ALERT_COLLISION = 'COLLISION'

LED_CLICK_STATUS = {
    1: GATE_ALERT_FLOODLIGHT_OVERRIDE, 
    2: GATE_ALERT_NO_MAIN_POWER,
    3: GATE_ALERT_BATTERY_LOW,
    4: GATE_ALERT_COLLISION
}


class SignalParser(object):
    def __init__(self):
        self.pin_sensor = Pin(PIN_SENSOR, Pin.IN)
        self.pin_sensor.irq(self.debounce_callback)
        self.last_click_on = 0
        self.last_alert = 0
        self.blink_counter = 0
        self.gate_alert = GATE_ALERT_OK
        self.debounce_timer = Timer(4)
        self.validation_timer = Timer(5)
        self.idle_timer = Timer(6)
        # Function local variable
        self._alert_status = GATE_ALERT_OK # in validate_state
        # Check current state
        self.gate_status = GATE_STATUS_OPEN if self.pin_sensor.value() == 0 else GATE_STATUS_CLOSED
        self.idle_timer.init(period=3000, callback=self.validate_idle_state, mode=Timer.ONE_SHOT)

    def debounce_callback(self, pin):
        self.debounce_timer.init(period=20, callback=self.debounce_timer_callback, mode=Timer.ONE_SHOT)
    
    def debounce_timer_callback(self, timer):
        if self.pin_sensor():
            schedule(self.trigger_callback, None)

    def trigger_callback(self, _):
        self.validation_timer.deinit()
        self.idle_timer.deinit()

        if ticks_diff(ticks_ms(), self.last_click_on) < ALERT_INERTVAL_TIME:
            self.blink_counter += 1
        else:
            self.blink_counter = 1

        self.last_click_on = ticks_ms()

        if self.blink_counter > 4:
            # opening or closing
            if self.gate_status == GATE_STATUS_CLOSED:
                self.gate_status = GATE_STATUS_OPENING
            if self.gate_status == GATE_STATUS_OPEN:
                self.gate_status = GATE_STATUS_CLOSING

        self.validation_timer.init(period=ALERT_INERTVAL_TIME, callback=self.validate_state, mode=Timer.ONE_SHOT)
        self.idle_timer.init(period=IDLE_INERTVAL_TIME, callback=self.validate_idle_state, mode=Timer.ONE_SHOT)

    def set_alert(self, alert):
        self.gate_alert = alert
        self.last_alert = ticks_ms()

    def validate_state(self, t):
        self._alert_status = LED_CLICK_STATUS.get(self.blink_counter, GATE_ALERT_OK)
        if self._alert_status != GATE_ALERT_OK:
            self.set_alert(self._alert_status)
            self.blink_counter = 0
            self.last_click_on = 0
            
    def validate_idle_state(self, t):
        self.gate_status = GATE_STATUS_CLOSED if self.pin_sensor() else GATE_STATUS_OPEN
        if  ticks_diff(ticks_ms(), self.last_alert) > ALERT_INERTVAL_TIME:
            self.gate_alert = GATE_ALERT_OK


async def sunlight_controller():
    while True:
        try:
            mqtt.publish_sunlight_status(PIN_LIGHT.read())
        except Exception as e:
            print(e)
        await sleep(1800)


def register_stauts_updater(sp):
    def updater():
        mqtt.publish_gate_status(sp.gate_status)
        mqtt.publish_alert_status(sp.gate_alert)
        mqtt.publish_sunlight_status(PIN_LIGHT.read())
    mqtt.set_sensor_status_callback(updater)


async def gate_controller():
    sp = SignalParser()
    status = sp.gate_status
    register_stauts_updater(sp)
    alert = sp.gate_alert
#    wdt = WDT()
    while True:
#        wdt.feed()
        if status != sp.gate_status:
            status = sp.gate_status
            mqtt.publish_gate_status(status)
        if alert != sp.gate_alert:
            alert = sp.gate_alert
            mqtt.publish_alert_status(alert)
        await sleep(1)
