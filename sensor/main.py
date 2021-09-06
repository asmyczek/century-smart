from sensor.sensor import sunlight_controller, gate_controller
from micropython import alloc_emergency_exception_buf
from uio import StringIO
import uasyncio, machine, time
import sensor.mqtt as mqtt
from besp import watch_network
import config

# Uncomment for debugging
alloc_emergency_exception_buf(100)

LOOP = None

# Periodically update sensor states
async def ping():
    while True:
        mqtt.CLIENT.update()
        await uasyncio.sleep(300)


# Exception handler
def exception_handler(loop, context):
    trace = StringIO()
    sys.print_exception(context["exception"], trace)  
    trace = trace.getvalue().split('\n')
    for s in trace:
        print(s)
    with open ('error.log', 'a') as f:
        for l in trace:
            f.write('{}\n'.format(l)) 

# Start all services
def start_service():
    print('Time: {}'.format(machine.RTC().datetime()))

    global LOOP

    LOOP = uasyncio.get_event_loop()
    LOOP.set_exception_handler(exception_handler)
    LOOP.create_task(mqtt.start_mqtt_client())
    time.sleep_ms(500)
    LOOP.create_task(ping())
    LOOP.create_task(watch_network())
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
