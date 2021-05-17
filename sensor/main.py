from sensor.sensor import sunlight_controller, gate_controller
import uasyncio, machine, time
import sensor.mqtt as mqtt
import config

LOOP = None

# Periodically update sensor states
async def ping():
    while True:
        mqtt.CLIENT.update()
        await uasyncio.sleep(300)


# Start all services
def start_service():
    print('Time: {}'.format(machine.RTC().datetime()))

    global LOOP

    LOOP = uasyncio.get_event_loop()
    LOOP.create_task(mqtt.start_mqtt_client())
    time.sleep_ms(500)
    LOOP.create_task(ping())
    LOOP.create_task(sunlight_controller())
    LOOP.create_task(gate_controller())

    print('Gate sensor started')
    try:
        LOOP.run_forever()
    except Exception as e:
        mqtt.CLIENT.publish_status('INTERRUPTED')
        mqtt.CLIENT.publish_error(e)
        print(e)
    finally:
        print('Gate sensor stopped.')
        LOOP.stop()
