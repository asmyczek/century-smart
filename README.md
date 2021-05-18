# century-smart[er]
Making Century gate motor a little smarter using ESP8266. The controller publishes mqtt messages for all status codes and triggers courtesy light as well as override. And for fun it has a tiny light sensor for morning and evening light automation with Home Assistant.

## Basic circuit 

As basic as it gets.

![](https://lh3.googleusercontent.com/pw/ACtC-3cMiDV3pL-4nnfi03rcoeL3vYCQoj7wbIp0Sp7k3ZtEbgJE7XXDKiF7Qaii9rEeEllti2vzJLOzFoSYxIrj2Mb-KV7pyyUvqeVSlHOmrEykI8seK_zrESmgO0PqTzoqxGY_shfrogku8F5Z1qqwPScz0w=w659-h541-no)


## Setup

1. Flash ESP with MicorPython. Currently I'm using version 1.14
2. Rename *config_example.py* to *config.py* and configure your WIFI and MQTT broker settings.
3. Push all Python files to ESP and ready to go.
4. In case of timing variations between models, adjust ALERT_INERTVAL_TIME which is the time between alert signals.

*cmd.py* contains helper functions to speed up work on webrepl.

## Home Assistant templates

```yaml
sensor:
  - platform: mqtt
    name: "Gate Status"
    state_topic: "stats/gate/gate/status"
    force_update: true

  - platform: mqtt
    name: "Gate Alert"
    state_topic: "stats/gate/alert/status"
    force_update: true

  - platform: mqtt
    name: "Gate Sunlight"
    state_topic: "stats/gate/sunlight/status"
    force_update: true


script:

  trigger_gate_floodlight:
    alias: Trigger Gate Light
    sequence:
    - service: mqtt.publish
      data:
        topic: "cmnd/gate/floodlight/trigger"
```