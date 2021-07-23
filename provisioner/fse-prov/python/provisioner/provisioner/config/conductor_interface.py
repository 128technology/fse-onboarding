"""
Helper module for reading/writing salt files and rsyncing them to the correct pod
"""

import logging
import pathlib

import attr
import yaml
import json

from provisioner import conductor, log_utils

LOG = logging.getLogger(__name__)

@attr.s
class ConductorInterface:
    """
    Class to handle all salt file management and synchronization

    Attrs:
        conductor_client (conductor.Client): Conductor client to retrieve the asset ID that
            corresponds to each entry ID

        pods_info (pods.Pods): Information for all pods
    """

    conductor_client = attr.ib(
        validator=[attr.validators.instance_of(conductor.Client)]
    )

    def upload_template_to_conductor(self, template_name, data, conductor_ip, force):
        """
        Writes the salt map files for each entry ID and adds each entry ID to the salt top file
        in the results reporter that has not encountered a failure, then syncs the salt files to
        the correct pod

        Args:
            results_reporter (results.Reporter): The results reporter where we retrieve
                the current database entry and record the results of the actions performed when
                writing map files

            pods_info (pods.Pods): Information for all pods

            salt_states (Iterable[str]): List of salt states to apply to each entry in the top.sls
        """
        try:
            template_data = self._read_file(template_name)
        except FileNotFoundError as err:
            raise TemplateNotFound(template_name, err)

        try:
            self.conductor_client.uplpoad_template(
                conductor_ip,
                template_name,
                template_data,
                data,
                force
                )
        except conductor.ConductorException as err:
            print(err)
            return None
        else:
            print(f"Uploaded template")


    def render_template(self, conductor_ip, template_name):

        try:
            query_response = self.conductor_client.render_template(
                conductor_ip,
                template_name
                )
        except conductor.ConductorException as err:
            print(err)
            return None
        else:
            LOG.debug(
                f"Render status {json.dumps(query_response)}"
            )

    def list_templates(self, conductor_ip):
        template_list = []

        try:
            query_response = self.conductor_client.list_templates(conductor_ip)
        except conductor.ConductorException as err:
            print(err)
            return None
        else:
            print(f"Queried list")
            for item in query_response:
                template_list.append(item['name'])
            return template_list


    def _read_file(self, file_name):
        template_path = pathlib.Path("/usr") / "share" / "128T-provisioner" / "config_templates" / file_name

        with open(template_path) as template_file:
            return template_file.read()

    def commit_candidate(self, conductor_ip):
        try:
            query_response = self.conductor_client.commit(conductor_ip)
        except conductor.ConductorException as err:
            print(err)
            return None
        else:
            LOG.debug(
                f"Render status {json.dumps(query_response)}"
            )



class TemplateNotFound(Exception):

    """
    Base Render Config Exception
    """

    def __init__(self, template_file, err):
        super().__init__(f"Could not find template file {template_file}: {err}")
