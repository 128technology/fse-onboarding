#!/bin/bash
export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8

CONFIG_TEMPLATES_DIR="/usr/share/128T-provisioner/config_templates/"
OUTPUT=$(ls ${CONFIG_TEMPLATES_DIR} | grep -v / | tr '\n' ' ')

# start the web app

# cd /var/www/fse-cmd-runner
# npm run start && initialize ${OUTPUT}

# Initialize templates to the conductor
# echo "${OUTPUT}"

initialize ${OUTPUT}
fse_add_store --use-test-db --force --render-template --perform-commit --template-name base base
