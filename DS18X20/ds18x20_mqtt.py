from umqtt.simple import MQTTClient
from time import sleep
import machine,esp,network,json,ubinascii
import onewire, ds18x20

esp.sleep_type(esp.SLEEP_LIGHT)
# the device is on GPIO14
dat = machine.Pin(2)

# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)

# Modify below section as required
CONFIG = {
     # Configuration details of the MQTT broker
     "MQTT_BROKER": "192.168.0.107",
     "USER": "",
     "PASSWORD": "",
     "PORT": 1883,
     # unique identifier of the chip
     "CLIENT_ID": b"esp8266_" + ubinascii.hexlify(machine.unique_id())
}
Topic1=b"esp4/sensor"
Topic2=b"esp4/time"
t=10

def sub_cb(topic, msg):
  global t
  t = msg

def connect_wifi():
  sta_if = network.WLAN(network.STA_IF)
  if not sta_if.isconnected():
    sta_if.active(True)
    sta_if.connect('Tenda_1F7DA0', 'aidpoy1505')
    while not sta_if.isconnected():
      pass
  global client
  client = MQTTClient(CONFIG['CLIENT_ID'], CONFIG['MQTT_BROKER'], user=CONFIG['USER'], password=CONFIG['PASSWORD'], port=CONFIG['PORT'])
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(Topic2)

while True:
  try:
    client.check_msg()
    ds.convert_temp()
    time.sleep(1)
    msg = json.dumps({
      'ID':CONFIG['CLIENT_ID'],
      'temperature':ds.read_temp(roms[0])
      })
    client.publish(Topic1,msg)
  except:
    connect_wifi()
    continue
  if type(t) is not int:
    t=int(t)
  sleep(t)
