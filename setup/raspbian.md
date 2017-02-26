# Setup on Raspbian

## Install the official supported operating system
Available from [Rasbian Jessie Lite](https://www.raspberrypi.org/downloads/raspbian/)

## Connect to your wireless network

Edit `/etc/wpa_supplicant/wpa_supplicant.conf` to add the SSID and pasword for your wireless network:

```
country=GB
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="SSID"
    psk="password"
}
```
Run `ifconfig wlan0` to verify that the settings were applied (you should see an IP address assigned now).  If not run `ifdown wlan0` and `ifup wlan0` to restart the wireless interface.

## Install Pre-requisites 
The default Python packaged with Ubuntu will not support TLS 1.2.  Perform an alt-install of the latest Python (at time of writing 2.7.12), an updated package manager (pip), the ibmiotf Python client library, and my fork of [python-lightify](https://github.com/durera/python-lightify/).  See: `install-raspbian.sh`


## Install the Gateway Application 
Download the client application code and supervisord configuration file.  See: `install-raspbian.sh`

```
mkdir -p /opt/ibm/gateway-lightify
cd /opt/ibm/gateway-lightify
wget https://raw.githubusercontent.com/ibm-watson-iot/gateway-lightify/master/gateway-lightify.py
wget https://raw.githubusercontent.com/ibm-watson-iot/gateway-lightify/master/supervisord/gateway-lightify.conf -O /etc/supervisor/conf.d/gateway-lightify.conf
```

## Update the supervisord configuration
You will need to set the IP address and username of the hub to connect to in gateway-lightify.conf:
```
[program:gateway-lightify]
directory = /opt/ibm/gateway-lightify
command = python2.7 gateway-lightify.py -c app.cfg  -i IP_ADDRESS
redirect_stderr = true
stdout_logfile = /var/log/supervisor/%(program_name)s.log
stdout_logfile_maxbytes = 10MB
stdout_logfile_backups=5
autorestart = true
```

## Create an application configuration file
After registering a Watson IoT Platform API key, create a configuration file with the correct details for the application `/opt/ibm/gateway-lightify/app.cfg`.

```
[application]
auth-key=$key
auth-token=$token
```

## Controlling the gateway application
Supervisor can be used to control the application using: `supervisorctl start|stop|restart|status gateway-lightify`
