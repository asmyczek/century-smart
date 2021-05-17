from network import WLAN, AP_IF, STA_IF
import gc, webrepl, esp
import config


esp.osdebug(None)
gc.collect()


# Setup network to connect to WIFI
def setup_network():
    # Disable ap
    ap_if = WLAN(AP_IF)
    ap_if.active(False)

    # Connect to home wifi
    wifi_if = WLAN(STA_IF)
    wifi_if.active(True)
    if not wifi_if.isconnected():
        wifi_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not wifi_if.isconnected():
            pass
    print('Network configuration:', wifi_if.ifconfig())


setup_network()
webrepl.start()
