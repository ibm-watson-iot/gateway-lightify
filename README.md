# IoT Gateway Application for OSRAM Lightify

Connect your OSRAM Lightify Hub to Watson IoT.

- [IBM Watson IoT](https://internetofthings.ibmcloud.com)
- [OSRAM Lightify](https://www.osram.com/lightify)

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

This version of the gateway only supports publishing state events.  Command control will be added in the future.
