#!/usr/bin/env bash

echo "Got argument $1"
/usr/share/128T-provisioner/scripts/list_templates
if [ $? -eq 0 ]
then
  echo "List Templates exited successfuly!"
fi
sleep 1
echo "Completed listing templates"
