"""
Module for gathering and reporting results
"""

import logging
import textwrap

from provisioner import log_utils

LOG = logging.getLogger(__name__)


class Reporter:
    """
    Keeps track of the steps performed on an each entry ID and their results
    """

    def __init__(self):
        self._results = {}

    def add_successful_step(self, entry_id, description):
        """
        Add a successful step performed on an entry ID to the results and
        set the overall result to a success

        Args:
            entry_id (str): The entry ID number

            description (str): The description of the step performed
        """
        LOG.debug(log_utils.create_log_context(entry_id, description))
        self._add_step(entry_id, description, success=True)

    def add_failed_step(self, entry_id, description):
        """
        Add a failed step performed on an entry ID to the results and
        set the overall result to a failure

        Args:
            entry_id (str): The entry ID number

            description (str): The description of the step that failed
        """
        log_utils.audit(
            LOG,
            log_utils.create_log_context(entry_id, description),
            level=logging.WARNING,
        )
        self._add_step(entry_id, description, success=False)

    def merge(self, other_reporter):
        """
        Merge steps for each entry_id from another results.Reporter

        Args:
            other_reporter (results.Reporter): The other reporter
        """
        for entry_id in other_reporter.get_entry_ids():
            for step in other_reporter.get_results()[entry_id]["steps"]:
                self._add_step(entry_id, step["description"], step["success"])

    def get_results(self):
        """
        Returns results

        Returns:
            dict: Dict of results keyed by entry ID
        """
        return self._results

    def get_entry_ids(self):
        """
        Returns entry IDs in results

        Returns:
            Iterable[str]: The entry IDs
        """
        return self._results.keys()

    def has_entry_hit_failure(self, entry_id):
        """
        Returns boolean indicating if the entry ID has hit a failure.

        Args:
            entry_id (str): The entry ID to check

        Returns:
            bool: True if entry ID has hit a failure
        """
        return not self._results[entry_id]["success"]

    def has_any_entry_hit_failure(self):
        """
        Returns boolean indicating if any entry ID has hit a failure.

        Returns:
            bool: True if any entry ID has hit a failure
        """
        return any(
            [self.has_entry_hit_failure(entry_id) for entry_id in self.get_entry_ids()]
        )

    def add_entry_data(self, entry_id, entry_data):
        """
        Add entry data to results

        Args:
            entry_id (str): The entry ID number to add results to

            entry_data (str): The entry data
        """
        try:
            self._results[entry_id]["entry_data"] = entry_data
        except KeyError:
            self._results[entry_id] = {}
            self._results[entry_id]["entry_data"] = entry_data

    def get_entry_data(self, entry_id):
        """
        Returns the entry data added to the results

        Args:
            entry_id (str): The entry ID number whose entry data to retrieve

        Returns:
            dict: The entry data
        """
        try:
            return self._results[entry_id]["entry_data"]
        except KeyError:
            return None

    def get_summary(self):
        """
        Get a summary string for the results in the format:

        Returns:
            str: the results, in summary format "[Entry ID]: [Success|Failure]"

            Example output:

                23423: Success
                12345: Success
                12346: Failure
        """

        def _form_short_result(entry_result):
            if entry_result["success"]:
                return "Success"

            try:
                for step in reversed(entry_result["steps"]):
                    if not step["success"]:
                        return f"Failure: {step['description']}"
            except KeyError:
                return "Failure"

        return "Results:\n" + textwrap.indent(
            "\n".join(
                f"{entry_id}: {_form_short_result(self._results[entry_id])}"
                for entry_id in self._results
            ),
            prefix="  ",
        )

    def get_details(self):
        """
        Create the full results in the form:

        Entry ID:
         - Step 1 description:                      Success/Failure
         - Step 2 description:                      Success/Failure

        Ex:

        23423:
         - Got info from DB:                        Success
         - Failed to edit config:                   Failure
        12345:
         - Got info from DB:                        Success
         - Pushed edit config:                      Success
         - Committed config:                        Success
         - Failed to write map files:               Failure
        12346:
         - Got info from DB:                        Success
         - Pushed edit config:                      Success
         - Committed config:                        Success
         - Wrote map files:                         Success
        """

        def _form_full_result(entry_result):
            return "\n".join(
                [
                    f" - {step['description'] + ':':<80}"
                    + ("Success" if step["success"] else "Failure")
                    for step in entry_result["steps"]
                ]
            )

        return "Results:\n" + textwrap.indent(
            "\n".join(
                f"{entry_id}:\n{_form_full_result(self._results[entry_id])}"
                for entry_id in self._results
            ),
            prefix="  ",
        )

    def _add_step(self, entry_id, description, success):
        step = {"success": success, "description": description}
        try:
            self._results[entry_id]["success"] &= success
            self._results[entry_id]["steps"].append(step)
        except KeyError:
            self._results[entry_id] = {}
            self._results[entry_id]["success"] = success
            self._results[entry_id]["steps"] = [step]
