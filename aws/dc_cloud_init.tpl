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

write_files:
- path: /root/preferences.json
  content: |
    {"_send_salt_events": false, "node-role": "combo", "node-name": "dummy-node", "router-name": "dummy-router", "conductor": {"primary": {"ip": "${conductor_address}"}}, "admin-password": "$6$M3M3HrbbfNmSZl79$Zk0vferU4FG5Y8SHDOlwphB6l3MHRVpgXT/ootnmRGrK.lRncmu4q7Z/no.u/OTmHowdv66Qdc2HW7pxMw.Qi1", "learn-from-ha-peer": false}
- path: /etc/salt/minion_id
  content: |
    l3niddc

runcmd:
- /bin/initialize128t -p /root/preferences.json
- systemctl enable 128T
- reboot
