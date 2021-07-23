"""
Abstract database client
"""

import abc

import attr


@attr.s
class BaseClient(metaclass=abc.ABCMeta):
    """
    Abstract base class for all database clients
    """

    @abc.abstractmethod
    def query_entry(self, entry_id):
        """
        Query database for entry by ID

        Args:
            entry_id (str): The database entry ID
        """

    @abc.abstractmethod
    def update_entry(self, entry):
        """
        Update an entry in the database

        Args:
            entry (Entry): The entry to update
        """
