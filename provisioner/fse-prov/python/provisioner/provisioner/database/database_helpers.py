"""
Helper module for querying databases, validating entries and reporting results
"""

import logging

from provisioner import log_utils, results
from provisioner.database import client


LOG = logging.getLogger(__name__)


def retrieve_and_validate_database_entry(
    database_client,
    entry_type,
    entry_ids
):
    """
    Retrieve and validate the database entries for the given entry IDs and adds the
    database entry to the results_reporter.

    Args:
        database_client (client.Client): The database client to query entries with

        entry_type (class Entry): The type to use to parse the database entry return data

        entry_ids (list[str]): A list of entry IDs to retrive from database

    Returns:
        results.Reporter: Contains the entry data, the record of the overall result of
            each entry and the result of each individual step performed on each entry
    """
    results_reporter = results.Reporter()

    for entry_id in entry_ids:
        database_entry = _query_database_for_entry_data(
            database_client, entry_type, results_reporter, entry_id
        )
        if database_entry is None:
            continue

        results_reporter.add_entry_data(entry_id, database_entry)

    return results_reporter

def _query_database_for_entry_data(
    database_client, entry_type, results_reporter, entry_id
):
    LOG.debug(log_utils.create_log_context(entry_id, "Querying database for entry"))
    try:
        database_entry = entry_type.query_for_entry(database_client, entry_id)
    except client.DatabaseException as err:
        results_reporter.add_failed_step(
            entry_id, f"Received error response getting entry from database: {err}",
        )
        return None
    else:
        results_reporter.add_successful_step(
            entry_id, f"Retrieved entry from database",
        )
        return database_entry
