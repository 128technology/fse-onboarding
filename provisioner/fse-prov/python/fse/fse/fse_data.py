"""
Common definitions for data used by other modules
"""

from provisioner import cli, conductor
from provisioner.config import conductor_interface

import click, yaml, pathlib

POD_MAP_FILE = pathlib.Path("/usr") / "share" / "128T-provisioner" / "provisioner.yml"

with open(POD_MAP_FILE, "r") as yaml_data:
    PROV_CONFIG_DATA = yaml.load(yaml_data, Loader=yaml.FullLoader)
    CONDUCTOR_IP = PROV_CONFIG_DATA["CONDUCTOR_IP"]
    USERNAME = PROV_CONFIG_DATA["USERNAME"]
    PASSWORD = PROV_CONFIG_DATA["PASSWORD"]

# USERNAME = "admin"
# PASSWORD = "128tRoutes"

CONDUCTOR_CLIENT = conductor.Client(
    username=USERNAME, password=PASSWORD, verify_https_certificate=False
)

# CONDUCTOR_IP = ["10.1.1.10", "10.1.1.100"]
REST_CONDUCTOR_INTERFACE = conductor_interface.ConductorInterface(CONDUCTOR_CLIENT)

STORE_TEMPLATE = "{:0>5}"

EDIT_CONFIG_TIMEOUT_SEC = 1200
COMMIT_CONFIG_TIMEOUT_SEC = 1200


def validate_stores(ctx, param, value):
    """
    Validate that at least one store was specified on the command line and format the
    store with the FSE store format

    Example usage:
        ```
        @click.command()
        @click.argument("stores", callback=fse_data.validate_stores, nargs=-1)
        def my_command(stores):
            for store in stores:
                print(store)
        ```
    """
    return [
        STORE_TEMPLATE.format(store) for store in cli.validate_stores(ctx, param, value)
    ]
