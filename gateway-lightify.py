import sys
import json
import time
import ibmiotf.application
from ibmiotf import APIException

import requests
import signal

import argparse
import logging
from logging.handlers import RotatingFileHandler

from lightify import Lightify


class Server():

	def __init__(self, args):
		# Setup logging - Generate a default rotating file log handler and stream handler
		fhFormatter = logging.Formatter('%(asctime)-25s %(levelname)-7s %(message)s')
		sh = logging.StreamHandler()
		sh.setFormatter(fhFormatter)
		
		self.version = "0.1.0"
		self.logger = logging.getLogger("server")
		self.logger.addHandler(sh)
		self.logger.setLevel(logging.DEBUG)
		
		self.options = ibmiotf.application.ParseConfigFile(args.config)
		
		self.lightifyTypeDescription = "Light connected to OSRAM Lightify Gateway"
		
		# Init IOTF client
		self.client = ibmiotf.application.Client(self.options, logHandlers=[sh])
		
		# Internal State
		self.knownDevices = {}
		self.knownDeviceTypes = {}

		# Init Hue properties
		self.lightifyAddress = args.ip
		
		self.username = ""
		self.password = ""
		self.serial   = ""
		
		#self._startLightifySession()
		
	def _startLightifySession(self):
		# Sorry, for initial version, only going to support EU -- session lasts for 15 minutes
		# Not actually used yet though
		
		headers = {"Content-Type": "application/json"}
		body = {
			"username": self.username,
			"password": self.password,
			"serialNumber": self.serial
		}
		
		r = requests.post("https://eu.lightify-api.org/lightify/services/session", headers=headers, data=json.dumps(body))
		# Check response code
		credentials = r.json();
		print(credentials)
	
	def _poll(self):
		self.lightify.update_all_light_status()
		lights = self.lightify.lights()
		for key in lights.keys():
			print(key)
			print(format(key, 'x'))
			print('-'.join(format(key, 'x')[i:i+2] for i in range(0,16,2)))

			light = lights[key]
			typeId = "lightify-%s" % light.type()
			deviceId = light.mac()
			
			# Register the device type if we need to
			if typeId not in self.knownDeviceTypes:
				try:
					deviceType = self.client.api.getDeviceType(typeId)
					self.knownDeviceTypes[typeId] = deviceType
				except APIException as e:
					self.logger.debug("ERROR [" + str(e.httpCode) + "] " + e.message)
					self.logger.info("Registering new device type: %s" % (typeId))
					
					deviceType = self.client.api.addDeviceType(typeId=typeId, description=None, deviceInfo=None)
					self.knownDeviceTypes[typeId] = deviceType
			
			# Register the device if we need to
			if deviceId not in self.knownDevices:
				try:
					device = self.client.api.getDevice(typeId, deviceId)
					self.knownDevices[deviceId] = device
				except APIException as e:
					self.logger.debug("ERROR [" + str(e.httpCode) + "] " + e.message)
					self.logger.info("Registering new device: %s:%s" % (typeId, deviceId))
					
					deviceMetadata = { "lightify-gateway": { "version": self.version } }
					deviceInfo = {"model": light.id(), "fwVersion" : light.fwVersion()}
					device = self.client.api.registerDevice(typeId, deviceId, authToken=None, deviceInfo=deviceInfo, location=None, metadata=deviceMetadata)
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
			from pprint import pprint
			print(state)
		
	
	def start(self):
		self.client.connect()
		self.lightify = Lightify(self.lightifyAddress)
		
		while True:
			self._poll()
			time.sleep(60)
		
		
	def stop(self):
		self.client.disconnect()
		

def interruptHandler(signal, frame):
	server.stop()
	sys.exit(0)


if __name__ == "__main__":
	signal.signal(signal.SIGINT, interruptHandler)

	# Initialize the properties we need
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', required=False)
	parser.add_argument('-i', '--ip', required=True)

	args, unknown = parser.parse_known_args()

	print("(Press Ctrl+C to disconnect)")

	server = Server(args)
	server.start()