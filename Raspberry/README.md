# Raspberry Pi Files used

## API Server
Server running for API CALLS

## Who's Home
whoshome.py for simple presence detection

### Setup 
You need to update your 'config.json' file to include the Name and Local IP address to monitor. 
Example config file:

```json
{
  "database": {
    "file": "whoshome.db"
  },
  "users": [
    {"name":"USERNAME", "ip":"LOCAL-IP-ADDRESS"},
    {"name":"Dawid", "ip":"192.168.1.1"}
  ]
}
```

# Setup
Add entries into the rc.local file:

```shell
sudo nano /etc/rc.local
```

```shell
# Startup Scripts
/home/pi/startup01.sh &
/home/pi/startup02.sh &
```

Startup Scripts content

```shell
# startup01.sh
#!/bin/sh
sleep 15

# Web Server API
sudo python /home/pi/Projects/HomeRemote/api.py
```

```shell
# startup02.sh
#!/bin/sh
sleep 15

# Who's Home Script
python /home/pi/Projects/HomeRemote/whoshome.py
```
