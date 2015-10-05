# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from tank_vendor.shotgun_api3 import Shotgun, ShotgunError
import threading
import urllib3
import certifi
import os
import urlparse
import logging
import requests

LOG = logging.getLogger("shotgun_api3")

class ThreadSafeShotgun(Shotgun):
    """
    Attempt to make a Shotgun handle thread safe with urllib3
    This is a TEMPORARY and HACKY workaround, the whole Shotgun API should be made
    thread safe.
    
    Code was taken from the Shotgun API, and connection and requests replaced with
    urllib3 calls.
    
    Downloads are not handled by this implementation.

    This implementation does not handle proxies and assume all
    requests are done through https
    """
    # A global lock that can be used in critical places to make them exclusive
    __lock = threading.Lock()

    def __init__(self, sg_handle):
        """
        Instantiate a thread safe handle from a regular one
        """
        super(ThreadSafeShotgun, self).__init__(
            base_url                    =   sg_handle.base_url,
            script_name                 =   sg_handle.config.script_name,
            api_key                     =   sg_handle.config.api_key,
            convert_datetimes_to_utc    =   sg_handle.config.convert_datetimes_to_utc,
            http_proxy=None,
            ensure_ascii=True,
            ca_certs=None,
            login                       =   sg_handle.config.user_login,
            password                    =   sg_handle.config.user_password,
            sudo_as_login               =   sg_handle.config.sudo_as_login,
            session_token               =   sg_handle.config.session_token,
            auth_token                  =   sg_handle.config.auth_token,
            connect                     =   False
        )

    def download_url(self, url, location):
        """
        Downloads a file from a given url.
        This method will take into account any proxy settings which have
        been defined in the Shotgun connection parameters.
        
        :param url: url to download
        :param location: path on disk where the payload should be written.
                         this path needs to exists and the current user needs
                         to have write permissions
        :returns: nothing
        """

        proxies = {}
        if self.config.proxy_server:
            # handle proxy auth
            if self.config.proxy_user and self.config.proxy_pass:
                auth_string = "%s:%s@" % (self.config.proxy_user, self.config.proxy_pass)
            else:
                auth_string = ""
            proxy_addr = "http://%s%s:%d" % (auth_string, self.config.proxy_server, self.config.proxy_port)
            proxies["http"] = proxy_addr
            proxies["https"] = proxy_addr
        try:
            response = requests.get(url, proxies=proxies)
            response.raise_for_status()
            # Write out the content into the given file
            f = open(location, "wb")
            try:
                f.write(response.content)
            finally:
                f.close()
        except Exception, e:
            raise ShotgunError("Could not download contents of url '%s'. Error reported: %s" % (url, e))

    def upload(self, entity_type, entity_id, path, field_name=None,
        display_name=None, tag_list=None):
        """Upload a file as an attachment/thumbnail to the specified
        entity_type and entity_id.

        :param entity_type: Required, entity type (string) to revive.

        :param entity_id: Required, id of the entity to revive.

        :param path: path to file on disk

        :param field_name: the field on the entity to upload to
            (ignored if thumbnail)

        :param display_name: the display name to use for the file in the ui
            (ignored if thumbnail)

        :param tag_list: comma-separated string of tags to assign to the file

        :returns: Id of the new attachment.
        """
        path = os.path.abspath(os.path.expanduser(path or ""))
        if not os.path.isfile(path):
            raise ShotgunError("Path must be a valid file, got '%s'" % path)

        is_thumbnail = (field_name == "thumb_image" or field_name == "filmstrip_thumb_image")

        params = {
            "entity_type": entity_type,
            "entity_id": entity_id,
        }

        params.update(self._auth_params())

        if is_thumbnail:
            url = urlparse.urlunparse((self.config.scheme, self.config.server,
                "/upload/publish_thumbnail", None, None, None))
            params["thumb_image"] = (
                os.path.basename(path),
                open(path, "rb").read(),
                "application/octet-stream"
            )
            if field_name == "filmstrip_thumb_image":
                params["filmstrip"] = True
        else:
            url = urlparse.urlunparse((self.config.scheme, self.config.server,
                "/upload/upload_file", None, None, None))
            if display_name is None:
                display_name = os.path.basename(path)
            # we allow linking to nothing for generic reference use cases
            if field_name is not None:
                params["field_name"] = field_name
            params["display_name"] = display_name
            # None gets converted to a string and added as a tag...
            if tag_list:
                params["tag_list"] = tag_list

            params["file"] = (
                os.path.basename(path),
                open(path, "rb").read(),
                "application/octet-stream"
            )

        http = urllib3.PoolManager(
                cert_reqs="CERT_REQUIRED", # Force certificate check.
                ca_certs=certifi.where(),  # Path to the Certifi bundle.
                )
        try:
            response = http.request_encode_body("POST", url, params)
            if response.status < 200 or response.status > 299: # Not ok
                raise ShotgunError("%d : Could not upload %s, to %s : %s" % (
                    response.status,
                    path,
                    url,
                    str(response),
                    ))
            result = response.data
            if not str(result).startswith("1"):
                raise ShotgunError("Could not upload file successfully, but "\
                    "not sure why.\nPath: %s\nUrl: %s\nError: %s" % (
                    path, url, str(result)))

            attachment_id = int(str(result).split(":")[1].split("\n")[0])
            return attachment_id
        except Exception, e:
            print str(e)
            raise

    def share_thumbnail(self, entities, thumbnail_path=None, source_entity=None,
        filmstrip_thumbnail=False, **kwargs):
        if not self.server_caps.version or self.server_caps.version < (4, 0, 0):
            raise ShotgunError("Thumbnail sharing support requires server "\
                "version 4.0 or higher, server is %s" % (self.server_caps.version,))

        if not isinstance(entities, list) or len(entities) == 0:
            raise ShotgunError("'entities' parameter must be a list of entity "\
                "hashes and may not be empty")

        for e in entities:
            if not isinstance(e, dict) or 'id' not in e or 'type' not in e:
                raise ShotgunError("'entities' parameter must be a list of "\
                    "entity hashes with at least 'type' and 'id' keys.\nInvalid "\
                    "entity: %s" % e)

        if (not thumbnail_path and not source_entity) or \
            (thumbnail_path and source_entity):
            raise ShotgunError("You must supply either thumbnail_path OR "\
                "source_entity.")

        # upload thumbnail
        if thumbnail_path:
            source_entity = entities.pop(0)
            if filmstrip_thumbnail:
                thumb_id = self.upload_filmstrip_thumbnail(source_entity['type'],
                    source_entity['id'], thumbnail_path, **kwargs)
            else:
                thumb_id = self.upload_thumbnail(source_entity['type'],
                    source_entity['id'], thumbnail_path, **kwargs)
        else:
            if not isinstance(source_entity, dict) or 'id' not in source_entity \
                or 'type' not in source_entity:
                raise ShotgunError("'source_entity' parameter must be a dict "\
                    "with at least 'type' and 'id' keys.\nGot: %s (%s)" \
                    % (source_entity, type(source_entity)))

        # only 1 entity in list and we already uploaded the thumbnail to it
        if len(entities) == 0:
            return thumb_id

        # update entities with source_entity thumbnail
        entities_str = []
        for e in entities:
            entities_str.append("%s_%s" % (e['type'], e['id']))
        # format for post request
        if filmstrip_thumbnail:
            filmstrip_thumbnail = 1
        params = {
            "entities": ','.join(entities_str),
            "source_entity": "%s_%s" % (source_entity['type'], source_entity['id']),
            "filmstrip_thumbnail": filmstrip_thumbnail,
        }

        params.update(self._auth_params())

        # Create opener with extended form post support
        url = urlparse.urlunparse((self.config.scheme, self.config.server,
            "/upload/share_thumbnail", None, None, None))
        http = urllib3.PoolManager(
                cert_reqs="CERT_REQUIRED", # Force certificate check.
                ca_certs=certifi.where(),  # Path to the Certifi bundle.
                )
        try:
            response = http.request_encode_body("POST", url, params)
            if response.status < 200 or response.status > 299: # Not ok
                raise ShotgunError("%d : Could not upload %s, to %s : %s" % (
                    response.status,
                    path,
                    url,
                    str(response),
                    ))
            result = response.data
            if not str(result).startswith("1"):
                raise ShotgunError("Unable to share thumbnail: %s" % result)
            else:
                # clearing thumbnail returns no attachment_id
                try:
                    attachment_id = int(str(result).split(":")[1].split("\n")[0])
                except ValueError:
                    attachment_id = None
            return attachment_id
        except Exception, e:
            raise

    def _get_connection(self):
        """Returns the current connection or creates a new connection to the
        current server.
        """
        if self._connection is not None:
            return self._connection

        if self.config.proxy_server:
            raise NotImplementedError("Proxies are not supported")
        else:
            self._connection = urllib3.PoolManager(
                    timeout=self.config.timeout_secs,
                    cert_reqs="CERT_REQUIRED", # Force certificate check.
                    ca_certs=certifi.where(),  # Path to the Certifi bundle.
                    )

        return self._connection

    def _close_connection(self):
        """Closes the current connection."""
        if self._connection is None:
            return

        self._connection.clear()
        self._connection = None
        return

    def _http_request(self, verb, path, body, headers):
        """Makes the actual HTTP request.
        """
        url = urlparse.urlunparse((self.config.scheme, self.config.server,
            path, None, None, None))
        LOG.debug("Request is %s:%s" % (verb, url))
        LOG.debug("Request headers are %s" % headers)
        LOG.debug("Request body is %s" % body)

        conn = self._get_connection()
        resp = conn.urlopen(verb, url, headers=headers, body=body)
        #http response code is handled else where
        http_status = (resp.status, "not supported")
        resp_headers = resp.getheaders()
        resp_body = resp.data

        LOG.debug("Response status is %s %s" % http_status)
        LOG.debug("Response headers are %s" % resp_headers)
        LOG.debug("Response body is %s" % resp_body)

        return (http_status, resp_headers, resp_body)

    def _build_opener(self, handler):
        """
        Build urllib2 opener with appropriate proxy handler.

        Revisited with some locks to avoid race conditions with
        urllib2 globals
        """
        try:
            self.__lock.acquire()
            if self.config.proxy_server:
                # handle proxy auth
                if self.config.proxy_user and self.config.proxy_pass:
                    auth_string = "%s:%s@" % (self.config.proxy_user, self.config.proxy_pass)
                else:
                    auth_string = ""
                proxy_addr = "http://%s%s:%d" % (auth_string, self.config.proxy_server, self.config.proxy_port)
                proxy_support = urllib2.ProxyHandler({self.config.scheme: proxy_addr})

                opener = urllib2.build_opener(proxy_support, handler)
            else:
                opener = urllib2.build_opener(handler)
            return opener
        finally:
            self.__lock.release()
