groups:
- t128
users:
- default
- name: t128
  primary-group: t128
  groups: wheel
  lock_passwd: False
  plain_text_passwd: 128tRoutes
chpasswd:
  list: |
    root:128tRoutes
  expire: False
disable_root: False
ssh_pwauth: True

runcmd:
- touch /home/centos/provisioner/provisioner/provisioner.yml

write_files:
- path: /root/preferences.json
  content: |
    {"_send_salt_events": false, "node-role": "conductor", "node-name": "node1", "router-name": "conductor", "admin-password": "$6$KQwR6rngigGE1t8v$9ec9/bRCgPJUQm74r9DsMwUlDt02oU3OssrsX4xWtBQJGngP.bSRxnm3nQKeZGlqWqkaiWEvWZDnrQ7mXJ1qK1", "learn-from-ha-peer": false, "disable-sizing": true}
- path: /etc/salt/minion_id
  content: |
    conductor
- path: /home/centos/provisioner/provisioner/provisioner.yml
  content: |
    CONDUCTOR_IP: ["${conductor_ip}"]
    USERNAME: "admin"
    PASSWORD: "128tRoutes"
- path: /home/centos/provisioner/provisioner/file_web_db.yml
  content: |
    HOST_IP: "${conductor_ip}"
- path: /home/centos/provisioner/database/base.yml
  content: |
    authority_name: "${authority_name}"
    conductor_address: "${conductor_ip}"
    dns_servers: ${dns_servers}
    interNodeSecurity: "${interNodeSecurity}"
    interRouterSecurity: "${interRouterSecurity}"
    lan_ipAddress: "${lan_ipAddress}"
    lan_pciAddress: "${lan_pciAddress}"
    lan_prefixLength: "${lan_prefixLength}"
    location: "${location}"
    locationCoordinates: "${locationCoordinates}"
    mgmt_gateway: "${mgmt_gateway}"
    mgmt_ipAddress: "${mgmt_ipAddress}"
    mgmt_pciAddress: "${mgmt_pciAddress}"
    mgmt_prefixLength: "${mgmt_prefixLength}"
    neighborhood_name: "${neighborhood_name}"
    ntp_servers: ${ntp_servers}
    routerName: "${routerName}"
    wan_gateway: "${wan_gateway}"
    wan_ipAddress: "${wan_ipAddress}"
    wan_pciAddress: "${wan_pciAddress}"
    wan_prefixLength: "${wan_prefixLength}"
    management_tenant: "${management_tenant}"
    wan_floating_ip: "${wan_floating_ip}"

runcmd:
- /bin/initialize128t -p /root/preferences.json
- systemctl enable 128T
- touch /lib/128technology/python/salt/file_roots/release.pem
- cd /home/centos/provisioner
- sleep 90
- export PROVISIONER_CONTAINER_VERSION=v0.0.1
- docker-compose up -d > dc.log 2>&1
- reboot
