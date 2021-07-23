"""
Utilities for making REST queries to a 128T Conductor.
"""

import json
import logging

import attr
import requests
import urllib3

LOG = logging.getLogger(__name__)


@attr.s
class Client:
    """
    Class used for querying a conductor

    Attrs:
        username (str): The username to login with

        password (str): The password to login with

        timeout (int): Timeout in seconds to wait for response

        retries (int): Number of retries to perform if request times out
    """

    username = attr.ib(validator=[attr.validators.instance_of(str)])
    password = attr.ib(validator=[attr.validators.instance_of(str)])
    timeout = attr.ib(default=60, validator=[attr.validators.instance_of(int)])
    retries = attr.ib(default=5, validator=[attr.validators.instance_of(int)])
    verify_https_certificate = attr.ib(
        default=True, validator=[attr.validators.instance_of(bool)]
    )

    def __attrs_post_init__(self):
        if not self.verify_https_certificate:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def query_asset_id(self, conductor_ip, router_name, node_name=None):
        """
        Query conductor for asset id of standalone router

        Args:
            conductor_ip (str): The conductor IP address

            router_name (str): The name of the router to query

            node_name (str | None): The name of the node to query, or None if standalone node

        Returns:
            str: the asset-id found for the given router and node

        Raises:
            AuthTimeout: There was a timeout authenticating with the conductor

            AuthError: There was an error authenticating with the conductor

            QueryTimeout: There was a timeout querying the conductor

            QueryError: There was an error querying the conductor

            QueryInvalidJson: The query returned invalid JSON

            AssetIdNotFound: The asset-id field was not found in the response
        """
        is_standalone_router = node_name is None

        url = (
            f"authority/router/{router_name}/node"
            if is_standalone_router
            else f"authority/router/{router_name}/node/{node_name}"
        )

        query_response_json = self.query_config(conductor_ip, url)

        try:
            return (
                query_response_json[0]["asset-id"]
                if is_standalone_router
                else query_response_json["asset-id"]
            )
        except (IndexError, KeyError):
            raise AssetIdNotFound(conductor_ip, router_name, query_response_json)

    def query_config(self, conductor_ip, config_url):
        """
        Query conductor for running config with a config url

        Args:
            conductor_ip (str): The conductor IP address

            config_url (str): The running config url to query for. The URL starts
                with the authority container: "authority/"

        Returns:
            dict: the parsed JSON response from the conductor

        Raises:
            AuthTimeout: There was a timeout authenticating with the conductor

            AuthError: There was an error authenticating with the conductor

            QueryTimeout: There was a timeout querying the conductor

            QueryError: There was an error querying the conductor

            QueryInvalidJson: The query returned invalid JSON
        """
        token = self._authenticate(conductor_ip)
        query_response_json = self._perform_query(conductor_ip, config_url, token)

        LOG.debug(f"Request result:\n{query_response_json}")

        return query_response_json

    def uplpoad_template(self, conductor_ip, template_name, template_data, variables, force):
        """
        Query conductor for running config with a config url

        Args:
            conductor_ip (str): The conductor IP address

            config_url (str): The running config url to query for. The URL starts
                with the authority container: "authority/"

        Returns:
            dict: the parsed JSON response from the conductor

        Raises:
            AuthTimeout: There was a timeout authenticating with the conductor

            AuthError: There was an error authenticating with the conductor

            QueryTimeout: There was a timeout querying the conductor

            QueryError: There was an error querying the conductor

            QueryInvalidJson: The query returned invalid JSON
        """
        url = f"https://{conductor_ip}/api/v1/template"
        url_patch = f"https://{conductor_ip}/api/v1/template/{template_name}"
        token = self._authenticate(conductor_ip)
        for retries_left in range(self.retries, 0, -1):
            LOG.debug(
                f"Authenticating with Conductor with {retries_left} retries remaining"
            )
            try:
                if force:
                    query_response = requests.patch(
                        url=url_patch,
                        json={
                            'name': template_name,
                            'description': 'uploaded from {}'.format(template_name),
                            'body': template_data,
                            'variables': variables,
                            },
                        headers={
                            "Authorization": f"Bearer {token}",
                        },
                        timeout=self.timeout,
                        verify=self.verify_https_certificate,
                    )
                else:
                    query_response = requests.post(
                        url=url,
                        json={
                            'name': template_name,
                            'description': 'uploaded from {}'.format(template_name),
                            'body': template_data,
                            'variables': variables,
                            'mode': "ADVANCED",
                            },
                        headers={
                            "Authorization": f"Bearer {token}",
                        },
                        timeout=self.timeout,
                        verify=self.verify_https_certificate,
                    )
            except requests.exceptions.Timeout:
                if retries_left == 1:
                    raise AuthTimeout(conductor_ip)
                continue

            if not (200 <= query_response.status_code < 300):
                if retries_left == 1:
                    if query_response.status_code == 401:
                        raise AuthError(conductor_ip, query_response)
                    else:
                        raise UnexpectedError(QueryInvalidJson, url, query_response)
                continue

            break


    def render_template(self, conductor_ip, template_name):
        """
        Query conductor for running config with a config url

        Args:
            conductor_ip (str): The conductor IP address

            config_url (str): The running config url to query for. The URL starts
                with the authority container: "authority/"

        Returns:
            dict: the parsed JSON response from the conductor

        Raises:
            AuthTimeout: There was a timeout authenticating with the conductor

            AuthError: There was an error authenticating with the conductor

            QueryTimeout: There was a timeout querying the conductor

            QueryError: There was an error querying the conductor

            QueryInvalidJson: The query returned invalid JSON
        """
        token = self._authenticate(conductor_ip)
        url = f"https://{conductor_ip}/api/v1/template/{template_name}/generate"
        for retries_left in range(self.retries, 0, -1):
            LOG.debug(
                f"Authenticating with Conductor with {retries_left} retries remaining"
            )
            try:
                query_response = requests.post(
                    url=url,
                    json=None,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}",
                    },
                    timeout=self.timeout,
                    verify=self.verify_https_certificate,
                )
            except requests.exceptions.Timeout:
                if retries_left == 1:
                    raise AuthTimeout(conductor_ip)
                continue

            if not (200 <= query_response.status_code < 300):
                if retries_left == 1:
                    if query_response.status_code == 401:
                        raise AuthError(conductor_ip, query_response)
                    else:
                        raise UnexpectedError(QueryInvalidJson, url, query_response)
                continue

            break

        try:
            query_response_json = query_response.json()
            status_reponse_json = self._check_for_completion(token, conductor_ip, template_name, query_response_json["id"])
            return status_reponse_json
        except (IndexError, KeyError):
            raise GenerationStatusIdNotFound(conductor_ip, template_name, query_response_json)

    def _check_for_completion(self, token, conductor_ip, template_name, id):
        url = f"https://{conductor_ip}/api/v1/template/{template_name}/generationStatus/{id}"
        header = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        complete = False
        retries_left = self.retries
        while (not complete) or (retries_left <= 0):
            LOG.debug(
                f"Sending request {url} to Conductor with {retries_left} retries remaining"
            )
            try:
                query_response = requests.get(
                    url,
                    headers=header,
                    timeout=self.timeout,
                    verify=self.verify_https_certificate,
                )
                complete = True if query_response.json()["status"] == "Finished" else False
                LOG.debug(
                    f"Percentage complete {query_response.json()['percentComplete']}, retries left {retries_left}"
                )
                retries_left -= 1
            except requests.exceptions.Timeout:
                retries_left -= 1
                if retries_left == 1:
                    raise QueryTimeout(conductor_ip, url)
                continue

            if not (200 <= query_response.status_code < 300):
                if retries_left == 1:
                    if query_response.status_code == 401:
                        raise AuthError(conductor_ip, query_response)
                    else:
                        raise UnexpectedError(QueryInvalidJson, url, query_response)
                continue

            break

        try:
            return query_response.json()
        except ValueError:
            raise QueryInvalidJson(conductor_ip, url, query_response)


    def commit(self, conductor_ip):
        """
        Query conductor for running config with a config url

        Args:
            conductor_ip (str): The conductor IP address

            config_url (str): The running config url to query for. The URL starts
                with the authority container: "authority/"

        Returns:
            dict: the parsed JSON response from the conductor

        Raises:
            AuthTimeout: There was a timeout authenticating with the conductor

            AuthError: There was an error authenticating with the conductor

            QueryTimeout: There was a timeout querying the conductor

            QueryError: There was an error querying the conductor

            QueryInvalidJson: The query returned invalid JSON
        """
        token = self._authenticate(conductor_ip)
        url = f"https://{conductor_ip}/api/v1/config/commit"
        for retries_left in range(self.retries, 0, -1):
            LOG.debug(
                f"Authenticating with Conductor with {retries_left} retries remaining"
            )
            try:
                query_response = requests.post(
                    url=url,
                    json=None,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}",
                    },
                    timeout=self.timeout,
                    verify=self.verify_https_certificate,
                )
            except requests.exceptions.Timeout:
                if retries_left == 1:
                    raise AuthTimeout(conductor_ip)
                continue

            if not (200 <= query_response.status_code < 300):
                if retries_left == 1:
                    raise AuthError(conductor_ip, query_response)
                continue

            break

        try:
            return query_response.json()
        except ValueError:
            raise QueryInvalidJson(conductor_ip, url, query_response)

    def list_templates(self, conductor_ip):
        token = self._authenticate(conductor_ip)
        url = f"https://{conductor_ip}/api/v1/template"
        header = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

        for retries_left in range(self.retries, 0, -1):
            LOG.debug(
                f"Sending request {url} to Conductor with {retries_left} retries remaining"
            )
            try:
                query_response = requests.get(
                    url,
                    headers=header,
                    timeout=self.timeout,
                    verify=self.verify_https_certificate,
                )
            except requests.exceptions.Timeout:
                if retries_left == 1:
                    raise QueryTimeout(conductor_ip, url)
                continue

            if not (200 <= query_response.status_code < 300):
                if retries_left == 1:
                    raise QueryError(conductor_ip, url, query_response)
                continue

            break

        try:
            return query_response.json()
        except ValueError:
            raise QueryInvalidJson(conductor_ip, url, query_response)

    def _authenticate(self, conductor_ip):
        for retries_left in range(self.retries, 0, -1):
            LOG.debug(
                f"Authenticating with Conductor with {retries_left} retries remaining"
            )
            try:
                auth_response = requests.post(
                    f"https://{conductor_ip}/api/v1/login",
                    json={"username": self.username, "password": self.password},
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    timeout=self.timeout,
                    verify=self.verify_https_certificate,
                )
            except requests.exceptions.Timeout:
                if retries_left == 1:
                    raise AuthTimeout(conductor_ip)
                continue

            if not (200 <= auth_response.status_code < 300):
                if retries_left == 1:
                    raise AuthError(conductor_ip, auth_response)
                continue

            break

        try:
            return auth_response.json()["token"]
        except (ValueError, KeyError):
            raise AuthError(conductor_ip, auth_response)

    def _perform_query(self, conductor_ip, config_url, token):
        url = f"https://{conductor_ip}/api/v1/config/running/{config_url}"
        header = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

        for retries_left in range(self.retries, 0, -1):
            LOG.debug(
                f"Sending request {url} to Conductor with {retries_left} retries remaining"
            )
            try:
                query_response = requests.get(
                    url,
                    headers=header,
                    timeout=self.timeout,
                    verify=self.verify_https_certificate,
                )
            except requests.exceptions.Timeout:
                if retries_left == 1:
                    raise QueryTimeout(conductor_ip, config_url)
                continue

            if not (200 <= query_response.status_code < 300):
                if retries_left == 1:
                    raise QueryError(conductor_ip, config_url, query_response)
                continue

            break

        try:
            return query_response.json()
        except ValueError:
            raise QueryInvalidJson(conductor_ip, config_url, query_response)


class ConductorException(Exception):

    """
    Base Conductor Exception
    """


class AuthTimeout(ConductorException):

    """
    An exception raised when the Conductor authorization times out
    """

    def __init__(self, conductor_ip):
        super().__init__(f"Conductor IP {conductor_ip} authentication timeout")


class AuthError(ConductorException):

    """
    An exception raised when the Conductor rejects authorization
    """

    def __init__(self, conductor_ip, auth_response):
        super().__init__(
            f"Conductor IP {conductor_ip} authentication error: {auth_response.text}",
        )


class QueryTimeout(ConductorException):

    """
    An exception raised when the query times out
    """

    def __init__(self, conductor_ip, query):
        super().__init__(
            f"Query timeout for query '{query}' returned from conductor IP {conductor_ip}",
        )


class QueryError(ConductorException):

    """
    An exception raised when the query returns an error response
    """

    def __init__(self, conductor_ip, query, query_response):
        super().__init__(
            f"Query error for query '{query}' returned from conductor IP {conductor_ip}: "
            f"{query_response.text}",
        )


class QueryInvalidJson(ConductorException):

    """
    An exception raised when the query returns invalid JSON
    """

    def __init__(self, conductor_ip, query, query_response):
        super().__init__(
            f"Query returned invalid json for query '{query}' returned from conductor IP "
            f"{conductor_ip}: {query_response}",
        )


class AssetIdNotFound(ConductorException):

    """
    An exception raised when the query response does not contain the asset ID
    """

    def __init__(self, conductor_ip, router_name, query_response_json):
        super().__init__(
            f"Router {router_name} asset ID not found in query to conductor IP {conductor_ip}: "
            f"{json.dumps(query_response_json)}",
        )

class UnexpectedError(ConductorException):

    """
    An exception raised when the query returns an error response
    """

    def __init__(self, conductor_ip, query, query_response):
        super().__init__(
            f"The server encountered an unexpected condition which prevented it from fulfilling the request.\n'{query}' returned from conductor IP {conductor_ip}: "
            f"{query_response.text}",
        )


class GenerationStatusIdNotFound(ConductorException):

    """
    An exception raised when the query response does not contain the asset ID
    """

    def __init__(self, conductor_ip, template_name, query_response_json):
        super().__init__(
            f"Generation Status Id Not Found for template {template_name} in query to conductor IP {conductor_ip}: "
            f"{json.dumps(query_response_json)}",
        )
