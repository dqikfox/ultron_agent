"""
connectors.py
==============

This module defines a simple connector interface and example implementations
for integrating the Ultron Agent with external systems.  A connector is
responsible for authenticating with a third-party service and exposing a
uniform set of methods for retrieving or storing data. Connectors can be
registered with the agent and used by tools or memory backends to access
external resources.

The base `Connector` class defines the minimal API for all connectors.
Specific connectors such as `GoogleDriveConnector` extend this interface
and provide concrete implementations. Additional connectors for services
like Slack, Gmail, or custom APIs can be added by following the same
pattern.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging


class Connector:
    """Abstract base class for all connectors.

    Subclasses should implement the `connect`, `fetch`, and
    `store` methods. These methods provide a high-level API for
    interacting with an external service. If a particular operation is
    unsupported, subclasses may raise ``NotImplementedError``.
    """

    name: str = "BaseConnector"
    description: str = "Base class for all connectors."

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.connected = False

    def connect(self) -> None:
        """Establish a connection to the external service.

        Concrete connectors should override this method to perform any
        authentication or setup required. For example, a Google Drive
        connector might load OAuth credentials here. By default this
        method simply marks the connector as connected.
        """
        logging.debug(f"[{self.name}] Connecting using config: {self.config}")
        self.connected = True

    def fetch(self, query: str) -> List[Any]:
        """Fetch data from the external service matching the given query.

        :param query: An arbitrary search string or identifier used to
            retrieve resources.
        :returns: A list of results.
        :raises NotImplementedError: if the connector does not support
            fetching data.
        """
        raise NotImplementedError(f"{self.name} does not implement fetch()")

    def store(self, data: Any, destination: Optional[str] = None) -> str:
        """Store data to the external service.

        :param data: Arbitrary data to upload or save.
        :param destination: Optional location within the service where the
            data should be stored.
        :returns: A string identifier for the stored resource (e.g. file ID).
        :raises NotImplementedError: if the connector does not support
            storing data.
        """
        raise NotImplementedError(f"{self.name} does not implement store()")


class GoogleDriveConnector(Connector):
    """Example connector for Google Drive.

    This connector uses the Google Drive API to list files, download
    documents, and upload new content. Authentication is performed lazily
    on first use; if the ``googleapiclient`` library is unavailable, the
    connector will operate in a degraded mode and simply log requests.
    """

    name = "GoogleDriveConnector"
    description = "Connector for accessing Google Drive files and folders."

    def __init__(self, credentials_path: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(kwargs)
        self.credentials_path = credentials_path
        self.service = None

    def connect(self) -> None:
        # Attempt to authenticate with Google Drive API. We avoid importing
        # googleapiclient at module import time to keep dependencies
        # optional. Users can install google-api-python-client if needed.
        logging.debug("[GoogleDriveConnector] Attempting to connect to Google Drive")
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            if not self.credentials_path:
                raise ValueError("Missing credentials_path for Google Drive connection")

            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=[
                    "https://www.googleapis.com/auth/drive.readonly",
                    "https://www.googleapis.com/auth/drive.file",
                ],
            )
            self.service = build('drive', 'v3', credentials=creds)
            self.connected = True
            logging.info("[GoogleDriveConnector] Connected to Google Drive API")
        except Exception as e:
            # Fallback: mark as connected but in offline mode
            logging.warning(
                f"[GoogleDriveConnector] Could not connect to Google Drive: {e}. Operating in offline mode."
            )
            self.connected = False

    def fetch(self, query: str) -> List[Dict[str, Any]]:
        """Search for files in Google Drive matching the query.

        If the API is unavailable, return an empty list and log the query.
        """
        logging.debug(f"[GoogleDriveConnector] Fetch called with query: {query}")
        if self.service:
            try:
                results = self.service.files().list(q=f"name contains '{query}'", pageSize=10).execute()
                return results.get('files', [])
            except Exception as e:
                logging.error(f"[GoogleDriveConnector] Error fetching files: {e}")
        # Offline or error: return empty list
        logging.info(f"[GoogleDriveConnector] Operating offline. Returning no results for query: {query}")
        return []

    def store(self, data: Any, destination: Optional[str] = None) -> str:
        """Upload a file to Google Drive."""
        logging.debug(f"[GoogleDriveConnector] Store called with data: {data}, destination: {destination}")
        if self.service and isinstance(data, str):
            try:
                from googleapiclient.http import MediaFileUpload

                file_metadata = {'name': data.split('/')[-1]}
                if destination:
                    file_metadata['parents'] = [destination]
                media = MediaFileUpload(data, resumable=True)
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                file_id = file.get('id', '')
                logging.info(f"[GoogleDriveConnector] Uploaded file, id: {file_id}")
                return file_id
            except Exception as e:
                logging.error(f"[GoogleDriveConnector] Error uploading file: {e}")
        # Offline or unsupported data type
        logging.info(f"[GoogleDriveConnector] Operating offline. Cannot upload {data}")
        return ''
