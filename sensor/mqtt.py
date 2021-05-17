from umqtt.robust import MQTTClient
import uasyncio, time, machine
import config


PIN_FLOOD_LIGHT = machine.Pin(config.PIN_FLOOD_LIGHT, machine.Pin.OUT)

FLOODLIGHT_ACTION = {
    'trigger' : 1,
    'override' : 4
}

class Client(object):

    def __init__(self):
        self._client = self._create_client()
        self.sensor_status_callback = None

    def _create_client(self):
        try:
            client = MQTTClient('terrarium',
                                config.MQTT_HOST,
                                user=config.MQTT_USER,
                                password=config.MQTT_PASSWORD,
                                port=config.MQTT_PORT)
            client.set_callback(self.on_message)
            if not client.connect(clean_session=False):
                print("MQTT new session being set up.")
            client.subscribe('cmnd/gate/#', qos=1)
            return client
        except Exception as e:
            print(e)
            return None

    def set_sensor_status_callback(self, callback):
        self.sensor_status_callback = callback

    def check_msg(self):
        self._client.check_msg()

    def on_message(self, topic, message):
        print('{} - {}'.format(topic, message))
        path = topic.decode("utf-8").split('/')
        if len(path) > 2 and path[2] == 'sync' and self.sensor_status_callback:
                self.sensor_status_callback()
        elif len(path) > 3 and path[2] == 'floodlight':
            trigger_time = FLOODLIGHT_ACTION.get(path[3], 0)
            if trigger_time > 0:
                PIN_FLOOD_LIGHT.value(1)
                time.sleep(trigger_time)
                PIN_FLOOD_LIGHT.value(0)

    def update(self):
        if self._client and self.sensor_status_callback:
            self.sensor_status_callback()

    def publish_sunlight_status(self, status):
        if self._client:
            self._client.publish(topic='stats/gate/sunlight/status', msg=str(status))

    def publish_gate_status(self, status):
        if self._client:
            self._client.publish(topic='stats/gate/gate/status', msg=status)

    def publish_alert_status(self, status):
        if self._client:
            self._client.publish(topic='stats/gate/alert/status', msg=status)

    def publish_error(self, error):
        if self._client:
            self._client.publish(topic='info/gate/error', msg=error)

CLIENT = Client()


async def start_mqtt_client():
    while True:
        CLIENT.check_msg()
        await uasyncio.sleep(1)

    CLIENT.disconnect()

