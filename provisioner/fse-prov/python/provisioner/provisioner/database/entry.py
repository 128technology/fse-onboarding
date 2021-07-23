"""
Database entry wrapper class created to define how to parse certain common
fields used by the rest of the provisioner
"""

import abc

import attr


@attr.s
class Entry(metaclass=abc.ABCMeta):
    """
    Abstract base class for all database entries

    Attrs:
        data (dict): The data for this database entry
    """

    data = attr.ib(validator=[attr.validators.instance_of(dict)])

    @classmethod
    def query_for_entry(cls, database_client, entry_id):
        return cls(data=database_client.query_entry(entry_id))

    @property
    @abc.abstractmethod
    def entry_id(self):
        """
        Returns the entry ID number
        """

    @property
    @abc.abstractmethod
    def pod(self):
        """
        Returns pod number
        """

    @pod.setter
    @abc.abstractmethod
    def pod(self, pod):
        """
        Sets the entry pod number
        """

    @property
    @abc.abstractmethod
    def event_state(self):
        """
        Returns the entry event state
        """

    @event_state.setter
    @abc.abstractmethod
    def event_state(self, event):
        """
        Set the entry event state
        """

    @property
    @abc.abstractmethod
    def router_name(self):
        """
        Returns the entry router name
        """

    @property
    @abc.abstractmethod
    def node_name(self):
        """
        Returns the entry node name, can return None if standalone node
        """
