import os
import sys
import json
import time
import signal
import logging
import traceback

from wiotp.sdk.application import ApplicationClient, parseEnvVars
from wiotp.sdk.api.registry.devices import DeviceInfo, DeviceCreateRequest
from lightify import Lightify


class Server():

	def __init__(self, ip, interval):
		# Setup logging - Generate a default rotating file log handler and stream handler
		fhFormatter = logging.Formatter('%(asctime)-25s %(levelname)-7s %(message)s')
		sh = logging.StreamHandler()
		sh.setFormatter(fhFormatter)
		
		self.version = "1.0.0"
		self.logger = logging.getLogger("server")
		self.logger.addHandler(sh)
		self.logger.setLevel(logging.INFO)
		
		self.options = parseEnvVars()
		
		self.lightifyTypeDescription = "Light connected to OSRAM Lightify Gateway"
		
		# Init IOTF client
		self.client = ApplicationClient(self.options, logHandlers=[sh])
		
		# Internal State
		self.knownDevices = {}
		self.knownDeviceTypes = {}

		# Init Hue properties
		self.lightifyAddress = ip
		self.logger.info("Connecting to Lightify at %s" % ip)

		self.pollingInterval = interval

		self.username = ""
		self.password = ""
		self.serial   = ""
		
		#self._startLightifySession()


	"""		
	def _startLightifySession(self):
		# Not actually used ... but kept for reference
		
		headers = {"Content-Type": "application/json"}
		body = {
			"username": self.username,
			"password": self.password,
			"serialNumber": self.serial
		}
		
		r = requests.post("https://eu.lightify-api.org/lightify/services/session", headers=headers, data=json.dumps(body))
		# Check response code
		credentials = r.json()
		print(credentials)
	"""

	def _poll(self):
		self.logger.info("Running poll loop (%s second interval) ... " % self.pollingInterval)
		self.lightify.update_all_light_status()
		lights = self.lightify.lights()
		for key in lights.keys():
			#print(key)
			#print(format(key, 'x'))
			#print('-'.join(format(key, 'x')[i:i+2] for i in range(0,16,2)))

			light = lights[key]
			typeId = "lightify-%s" % light.type()
			deviceId = light.mac()
			
			deviceRegistry = self.client.registry
			# Register the device type if we need to
			if typeId not in self.knownDeviceTypes:
				if typeId in deviceRegistry.devicetypes:
					deviceType = deviceRegistry.devicetypes[typeId]
					self.knownDeviceTypes[typeId] = deviceType
				else:
					self.logger.info("Registering new device type: %s" % (typeId))
					deviceType = deviceRegistry.devicetypes.create({"id": typeId})
					self.knownDeviceTypes[typeId] = deviceType
			
			# Register the device if we need to
			if deviceId not in self.knownDevices:
				if deviceId in deviceRegistry.devicetypes[typeId].devices:
					device = deviceRegistry.devicetypes[typeId].devices[deviceId]
					self.knownDevices[deviceId] = device
				else:
					self.logger.info("Registering new device: %s:%s" % (typeId, deviceId))
					
					createData = DeviceCreateRequest(
						typeId=typeId, 
						deviceId=deviceId, 
						deviceInfo=DeviceInfo(model=light.id(), fwVersion=light.fwVersion()),
						metadata={ "lightify-gateway": { "version": self.version } }
					)

					device = deviceRegistry.devices.create(createData)
					self.knownDevices[deviceId] = device
			
			state = {
				"online": True if light.online() == 1 else False,
				"on": True if light.on() == 1 else False,
				"lum": light.lum(),
				"temp": light.temp(),
				"colour": {
					"red": light.red(),
					"green": light.green(),
					"blue": light.blue()
				},
				"alpha": light.alpha(),
			}
		
			# Publish the current state of the light
			self.client.publishEvent(typeId, deviceId, "state", "json", state)
			self.logger.debug("Published event for %s:%s: %s" % (typeId, deviceId, json.dumps(state)))
		
	
	def start(self):
		self.client.connect()
		self.lightify = Lightify(self.lightifyAddress)
		
		while True:
			try:
				self._poll()
				time.sleep(self.pollingInterval)
			except Exception as e:
				error = traceback.format_exc()
				self.logger.info("Exiting: Caught exception: %s\n%s" % (e, error))
				sys.exit(1)

	def stop(self):
		self.client.disconnect()
		

def interruptHandler(signal, frame):
	server.stop()
	sys.exit(0)


if __name__ == "__main__":
	signal.signal(signal.SIGINT, interruptHandler)

	ipAddr   = os.getenv("LIGHTIFY_IP")
	interval = os.getenv("INTERVAL", "60")

	print("(Press Ctrl+C to disconnect)")

	server = Server(ipAddr, int(interval))
	server.start()