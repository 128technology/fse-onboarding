"""
Client for MSR databases
"""

import logging

from provisioner.database import base_client

import attr
import requests
import urllib3

LOG = logging.getLogger(__name__)


@attr.s
class Client(base_client.BaseClient):
    """
    Class used to access the database

    Attrs:
        entry_url_template (str): The url template used to get a database entry by ID
            templated by entry ID, e.g. https://customer.database.com/entry/v1.0/router/{}

        timeout (int): Timeout in seconds to wait for response

        retries (int): Number of retries to perform if request times out
    """

    entry_url_template = attr.ib(validator=[attr.validators.instance_of(str)])
    timeout = attr.ib(default=60, validator=[attr.validators.instance_of(int)])
    retries = attr.ib(default=5, validator=[attr.validators.instance_of(int)])
    verify_https_certificate = attr.ib(
        default=True, validator=[attr.validators.instance_of(bool)]
    )

    def __attrs_post_init__(self):
        if not self.verify_https_certificate:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def query_entry(self, entry_id):
        """
        Override

        Query database for entry by ID

        Args:
            entry_id (str): The database entry ID

        Returns:
            dict: The data returned by the database

        Raises:
            DatabaseTimeout: There was a timeout querying the database

            DatabaseError: There was an error querying the database

            DatabaseInvalidJson: The query returned invalid JSON
        """
        url = self.entry_url_template.format(entry_id)
        for retries_left in range(self.retries, 0, -1):
            LOG.debug(
                f"Querying database {url} for entry {entry_id} with {retries_left} retries remaining"
            )

            try:
                query_response = requests.get(
                    url, timeout=self.timeout, verify=self.verify_https_certificate
                )
            except requests.exceptions.Timeout:
                if retries_left == 1:
                    raise DatabaseTimeout(entry_id)
                continue
            except requests.exceptions.ConnectionError:
                raise DatabaseConnectionError(entry_id)

            if not (200 <= query_response.status_code < 300):
                if retries_left == 1:
                    raise DatabaseError(entry_id, query_response)
                continue

            break

        try:
            return query_response.json()
        except ValueError:
            raise DatabaseInvalidJson(entry_id, query_response.text)

    def update_entry(self, entry):
        """
        Override

        Update an entry in the database

        Args:
            entry (Entry): The entry to update

        Raises:
            DatabaseTimeout: There was a timeout querying the database

            DatabaseError: There was an error querying the conductor
        """
        entry_id = entry.entry_id
        url = self.entry_url_template.format(entry_id)
        for retries_left in range(self.retries, 0, -1):
            LOG.debug(
                f"Updating database {url} for entry {entry_id} with {retries_left} retries remaining"
            )
            try:
                query_response = requests.post(
                    url,
                    timeout=self.timeout,
                    json=entry.data,
                    verify=self.verify_https_certificate,
                )
            except requests.exceptions.Timeout:
                if retries_left == 1:
                    raise DatabaseTimeout(entry_id)
                continue

            if not (200 <= query_response.status_code < 300):
                if retries_left == 1:
                    raise DatabaseError(entry_id, query_response)
                continue

            break


class DatabaseException(Exception):

    """
    Base Database Exception
    """


class DatabaseTimeout(DatabaseException):

    """
    An exception raised when a database query times out
    """

    def __init__(self, entry_id):
        super().__init__(f"Query timeout to database for entry ID {entry_id}")


class DatabaseConnectionError(DatabaseException):

    """
    An exception raised when there an issue connecting to the database
    """

    def __init__(self, entry_id):
        super().__init__(f"Connection error to database for entry ID {entry_id}")


class DatabaseError(DatabaseException):

    """
    An exception raised when a database query returns an error response
    """

    def __init__(self, entry_id, query_response):
        super().__init__(
            f"Query error returned from database for entry ID {entry_id}: {query_response.text}"
        )


class DatabaseInvalidJson(DatabaseException):

    """
    An exception raised when a database query returns invalid JSON
    """

    def __init__(self, entry_id, query_response_data, reason=""):
        super().__init__(
            f"Query error returned invalid json for entry ID {entry_id}: {reason}, data={query_response_data}"
        )
