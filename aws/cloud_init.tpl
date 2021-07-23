groups:
- t128
users:
- default
- name: t128
  primary-group: t128
  groups: wheel
  lock_passwd: False
#  plain_text_passwd: 128tRoutes
#chpasswd:
#  list: |
#    root:128tRoutes
#  expire: False
disable_root: False
#ssh_pwauth: True
