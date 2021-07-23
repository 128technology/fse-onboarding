# CVS Automation Web App

This provides a simple web app wrapper around automation tools.

## Install
Make sure contents of `web` are in `/srv/salt`.

Place the `automation-web.service` file in `/usr/lib/systemd/system/automation-web.service`.

Start the `automation-web` service with:
```
sudo systemctl start automation-web
```

## Debug
Debug any issues with:
```
journalctl -u automation-web
```
