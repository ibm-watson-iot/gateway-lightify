# IoT Gateway Application for OSRAM Lightify

[![Build Status](https://travis-ci.org/ibm-watson-iot/gateway-lightify.svg?branch=master)](https://travis-ci.org/ibm-watson-iot/gateway-lightify)


Connect your OSRAM Lightify Hub to Watson IoT.

- [IBM Watson IoT](https://internetofthings.ibmcloud.com)
- [WIoTP Python SDK](https://github.com/ibm-watson-iot/iot-python)
- [OSRAM Lightify](https://www.osram.com/lightify)


## Usage

All configuration is handled via environment variables:
- You need to provide the API key and token to use when connecting to Watson IoT Platform.
- You need to provide the IP address of your Lightify Hub on the local network
- Optionally, you can override the default (60 second) polling inverval

```
export WIOTP_API_KEY=xxx
export WIOTP_API_TOKEN=xxx
export LIGHTIFY_IP=xxx
export INTERVAL=60
python src/gateway-lightify.py
```

## Docker

The gateway is packaged into a convenient docker image for ease of use: [wiotp/gateway-lightify](https://hub.docker.com/r/wiotp/gateway-lightify/)

```
export WIOTP_API_KEY=xxx
export WIOTP_API_TOKEN=xxx
export LIGHTIFY_IP=xxx
export INTERVAL=60

docker run wiotp/gateway-lightify -e WIOTP_API_KEY -e WIOTP_API_TOKEN -e LIGHTIFY_IP -e INTERVAL
```


## Lights

### Automatic Device Registration

Any new light connected to your Lightify hub will be auto-registered as a new device in Watson IoT

### Events

State updates are published to Watson IoT every 60 seconds (althought this can easily be changed).  For every light connected to your hub the 
gateway will relay a state event containing all the state data available from Lightify:

 
```json
{
  "online": true,
  "on": true,
  "lum": 100,
  "temp": 2702,
  "colour": {
    "red": 1,
    "green": 0,
    "blue": 0,
  },
  "alpha": 255
}
```

### Commands

This version of the gateway only supports publishing state events.  Command control may be added in the future.
