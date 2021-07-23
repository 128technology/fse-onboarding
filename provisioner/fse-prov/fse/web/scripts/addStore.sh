#!/usr/bin/env bash

echo "Got argument $1"
/usr/share/128T-provisioner/scripts/fse_add_store --render-template --use-test-db --template-name sample $1
if [ $? -eq 0 ]
then
  echo "Add store exited successfuly!"
fi
sleep 1
echo "Completed adding store"
