"""
Client for FSE MSR databases
"""

import logging

from provisioner.database import client, entry

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_MASTER_DB_STORE_PARAM_TEMPLATE_URL = "http://web:5000/api/v1/stores?id={}"

_TEST_DB_STORE_PARAM_TEMPLATE_URL = "http://web:5000/api/v1/stores?id={}"

_DB_TIMEOUT_SEC = 60
_DB_RETRIES = 5

LOG = logging.getLogger(__name__)


class FseEntry(entry.Entry):
    """
    Class for FSE database entries
    """

    @property
    def entry_id(self):
        """Override"""
        return self.data["storeNumber"]

    @property
    def pod(self):
        """Override"""
        return self.data["pod"]

    @pod.setter
    def pod(self, pod):
        """Override"""
        self.data["pod"] = str(pod)

    @property
    def event_state(self):
        """Override"""
        return self.data["eventState"]

    @event_state.setter
    def event_state(self, event):
        """Override"""
        self.data["eventState"] = str(event)

    @property
    def router_name(self):
        """Override"""
        return self.data["storeId"]

    @property
    def node_name(self):
        """Override"""
        return None


class FseClient(client.Client):
    """
    Class used for accessing the FSE database

    This class is only required because the FSE database does not behave like a normal
    CRUD API.

    To retrieving an entry for a resource perform a GET to this URL:

    https://rxa-128mrec.stores.fse.com/store/v2.0/router-config/<resource-id>

    However, to update the entry at a specific resource perform a POST to this URL:

    https://rxa-128mrec.stores.fse.com/store/v2.0/router-config

    With the data being a list of the resources to update. Their database has internal
    logic to look for the store number and update the appropriate resource, which only
    makes this logic more complicated.
    """

    def update_entry(self, entry):
        """
        Update an entry in the database

        Args:
            entry (Entry): The entry to update

        Raises:
            DatabaseTimeout: There was a timeout querying the database

            DatabaseError: There was an error querying the conductor
        """
        entry_id = entry.entry_id
        url = _MASTER_DB_STORE_URL
        for retries_left in range(self.retries, 0, -1):
            LOG.debug(
                f"Updating database {url} for entry {entry_id} with {retries_left} retries remaining"
            )
            try:
                query_response = requests.post(
                    url, timeout=self.timeout, json=[entry.data], verify=False,
                )
            except requests.exceptions.Timeout:
                if retries_left == 1:
                    raise database.DatabaseTimeout(entry_id)
                continue

            if not (200 <= query_response.status_code < 300):
                if retries_left == 1:
                    raise database.DatabaseError(entry_id, query_response)
                continue

            break


PROD_DATABASE_CLIENT = FseClient(
    entry_url_template=_MASTER_DB_STORE_PARAM_TEMPLATE_URL,
    timeout=_DB_TIMEOUT_SEC,
    retries=_DB_RETRIES,
    verify_https_certificate=False,
)

TEST_DATABASE_CLIENT = FseClient(
    entry_url_template=_TEST_DB_STORE_PARAM_TEMPLATE_URL,
    timeout=_DB_TIMEOUT_SEC,
    retries=_DB_RETRIES,
    verify_https_certificate=False,
)
