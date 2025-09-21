import json
import logging
import os
import uuid
from collections import deque
import typing

# Optional Google Drive integration imports are performed lazily inside the helper

class Memory:
    def __init__(self, short_term_limit=10, long_term_file='long_term_memory.json'):
        """Initialize Memory with optional Google Drive persistence.

        Drive persistence is disabled by default; enable it by setting
        MEMORY_USE_GOOGLE_DRIVE=1 and providing SERVICE_ACCOUNT_FILE and/or
        DRIVE_FOLDER_ID environment variables. When DRIVE_FOLDER_ID is not set,
        the code will fall back to the user-supplied shared folder id.
        """
        self.short_term_memory = deque(maxlen=short_term_limit)
        self.long_term_file = long_term_file

        # Drive integration is disabled by default. Enable by setting env var
        # MEMORY_USE_GOOGLE_DRIVE=1 and providing DRIVE_FOLDER_ID and
        # SERVICE_ACCOUNT_FILE (or GOOGLE_SERVICE_ACCOUNT_JSON path).
        self.use_drive = os.environ.get('MEMORY_USE_GOOGLE_DRIVE', '0') == '1'

        # Use DRIVE_FOLDER_ID env var if provided, otherwise fall back to the
        # explicit folder id supplied by the user (shared link). You can still
        # override by setting DRIVE_FOLDER_ID in your environment.
        self.drive_folder_id = os.environ.get('DRIVE_FOLDER_ID') or '1FCDNN-QW8JdSMAfuUsXTRtXsACj5E5n9'
        # If you have a local Google Drive mount (eg. Backup and Sync or Drive for Desktop)
        # you can set DRIVE_LOCAL_PATH to a path like 'G:\\My Drive\\Z\\X' and the
        # memory system will copy the JSON to that folder instead of using the
        # Drive HTTP API. We also accept DRIVE_FOLDER_ID as a local path.
        self.local_drive_path = os.environ.get('DRIVE_LOCAL_PATH')
        self.service_account_file = os.environ.get('SERVICE_ACCOUNT_FILE') or os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')

        if self.use_drive:
            logging.info('Google Drive memory persistence enabled (MEMORY_USE_GOOGLE_DRIVE=1).')
            # Support two modes:
            # 1) Local-mounted Drive folder (DRIVE_LOCAL_PATH or DRIVE_FOLDER_ID pointing to a path)
            # 2) Remote Google Drive API using a service account or OAuth
            try:
                # Prefer explicit DRIVE_LOCAL_PATH
                local_path = self.local_drive_path or None
                # If DRIVE_FOLDER_ID looks like an absolute path (Windows drive letter or path sep)
                if not local_path and self.drive_folder_id:
                    # treat values like 'G:\\' or 'G:/My Drive/...' as a local path
                    if os.path.isabs(self.drive_folder_id) or (':' in self.drive_folder_id and ('\\' in self.drive_folder_id or '/' in self.drive_folder_id)):
                        local_path = self.drive_folder_id

                if local_path:
                    # initialize local path helper; create folder if missing
                    self._drive_helper = LocalDriveMemory(local_path)
                    logging.info('Using local Drive folder for memory persistence: %s', local_path)
                else:
                    # remote Drive API: requires service account or OAuth
                    if not self.drive_folder_id or not self.service_account_file:
                        logging.warning('Drive enabled but DRIVE_FOLDER_ID or SERVICE_ACCOUNT_FILE not set; disabling drive persistence.')
                        self.use_drive = False
                    else:
                        self._drive_helper = GoogleDriveMemory(self.service_account_file, self.drive_folder_id)
            except Exception:
                logging.exception('Failed to initialize Drive persistence helper. Disabling drive persistence.')
                self.use_drive = False

        # Load long-term memory (from local file or Drive if enabled).
        self.long_term_memory = self.load_long_term_memory(long_term_file)
        logging.info("Memory initialized with shortterm and longterm storage. - memory.py:34")

    def load_long_term_memory(self, file_path):
        # Normal local load
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                logging.exception('Failed to read long term memory file locally; continuing with empty memory.')
                return {}

        # If not found locally and Drive is enabled, try to download
        if os.environ.get('MEMORY_USE_GOOGLE_DRIVE', '0') == '1':
            # honor DRIVE_FOLDER_ID env var if set; otherwise use the same
            # default fallback configured at init
            drive_folder_id = os.environ.get('DRIVE_FOLDER_ID') or '1FCDNN-QW8JdSMAfuUsXTRtXsACj5E5n9'
            service_account = os.environ.get('SERVICE_ACCOUNT_FILE') or os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
            if drive_folder_id and service_account:
                try:
                    helper = GoogleDriveMemory(service_account, drive_folder_id)
                    helper.download_file(file_path)
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return json.load(f)
                except Exception:
                    logging.exception('Failed to download memory from Google Drive')

        return {}

    def save_long_term_memory(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.long_term_memory, f, ensure_ascii=False, indent=2)
        except Exception:
            logging.exception('Failed to save long term memory locally')

        # If Drive is enabled, attempt to upload/update the file
        if getattr(self, 'use_drive', False):
            try:
                self._drive_helper.upload_file(file_path)
            except Exception:
                logging.exception('Failed to upload long term memory to Google Drive')

    def add_to_short_term(self, item):
        self.short_term_memory.append(item)
        logging.info(f"Added to shortterm memory: {item} - memory.py:80")

    def add_to_long_term(self, item):
        item_id = str(uuid.uuid4())
        self.long_term_memory[item_id] = item
        logging.info(f"Added to longterm memory: {item_id} > {item} - memory.py:85")
        # Persist after adding
        try:
            self.save_long_term_memory(self.long_term_file)
        except Exception:
            logging.exception('Failed to persist long term memory after add')

    def retrieve_short_term(self):
        return list(self.short_term_memory)

    def retrieve_long_term(self):
        return self.long_term_memory

    def clear_short_term(self):
        self.short_term_memory.clear()
        logging.info("Cleared shortterm memory. - memory.py:100")

    def clear_long_term(self):
        self.long_term_memory.clear()
        logging.info("Cleared longterm memory. - memory.py:104")

    def get_recent_memory(self, limit=5):
        """Get recent memory items for agent network queries"""
        recent_items = []

        # Get recent short-term memory
        short_term_items = list(self.short_term_memory)
        recent_items.extend(short_term_items[-limit:])

        # Get recent long-term memory if needed
        if len(recent_items) < limit:
            long_term_items = list(self.long_term_memory.values())
            remaining = limit - len(recent_items)
            recent_items.extend(long_term_items[-remaining:])

        return recent_items[:limit]

    def search_memory(self, query):
        """Search memory for relevant items"""
        results = []
        query_lower = query.lower()

        # Search short-term memory
        for item in self.short_term_memory:
            if isinstance(item, str) and query_lower in item.lower():
                results.append(item)
            elif isinstance(item, dict) and any(query_lower in str(v).lower() for v in item.values()):
                results.append(item)

        # Search long-term memory
        for item in self.long_term_memory.values():
            if isinstance(item, str) and query_lower in item.lower():
                results.append(item)
            elif isinstance(item, dict) and any(query_lower in str(v).lower() for v in item.values()):
                results.append(item)

        return results


class GoogleDriveMemory:
    """Optional Google Drive helper using a service account JSON file.

    Notes:
    - This helper is optional and requires the `google-api-python-client` and `google-auth` packages.
    - Provide a service account JSON path via SERVICE_ACCOUNT_FILE or GOOGLE_SERVICE_ACCOUNT_JSON env var.
    - The DRIVE_FOLDER_ID env var must be set to the Drive folder where memory files will be stored.
    """

    def __init__(self, service_account_file: str, folder_id: str):
        # Lazy imports so the main module doesn't require google libs unless used
        # Try several authentication flows to make Drive persistence robust in
        # different environments (service account, application default creds,
        # and interactive user OAuth). Keep imports lazy so optional deps are
        # only required when Drive is used.
        try:
            # core libs
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
        except Exception as e:
            raise ImportError('Google Drive dependencies missing. Install: pip install google-api-python-client google-auth google-auth-oauthlib') from e

        self.folder_id = folder_id
        scopes = ['https://www.googleapis.com/auth/drive']

        creds = None

        # 1) Try service account JSON if provided
        if service_account_file:
            try:
                from google.oauth2 import service_account

                logging.debug('Attempting Google Drive auth via service account file: %s', service_account_file)
                creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
            except Exception:
                logging.exception('Service account authentication failed (will try other methods)')

        # 2) Try Application Default Credentials (useful on GCE / Cloud Shell / ADC setup)
        if creds is None:
            try:
                import google.auth

                logging.debug('Attempting Application Default Credentials for Google Drive')
                adc_creds, _ = google.auth.default(scopes=scopes)
                if adc_creds:
                    creds = adc_creds
            except Exception:
                logging.debug('Application Default Credentials not available or failed')

        # 3) As a last resort, try an interactive InstalledAppFlow if a
        # client secrets file is provided via GOOGLE_OAUTH_CLIENT_SECRETS env var.
        if creds is None:
            try:
                from google_auth_oauthlib.flow import InstalledAppFlow

                client_secrets = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRETS')
                token_cache = os.environ.get('GOOGLE_OAUTH_TOKEN_FILE') or os.path.join(os.path.expanduser('~'), '.ultron_drive_token.json')
                if client_secrets and os.path.exists(client_secrets):
                    logging.info('No service account or ADC available; running InstalledAppFlow using %s', client_secrets)
                    flow = InstalledAppFlow.from_client_secrets_file(client_secrets, scopes=scopes)
                    creds = flow.run_local_server(port=0)
                    # persist token for future runs
                    try:
                        with open(token_cache, 'w', encoding='utf-8') as tf:
                            tf.write(creds.to_json())
                        logging.info('Saved interactive Drive token to %s', token_cache)
                    except Exception:
                        logging.debug('Failed to save Drive token; continuing without cache')
                else:
                    logging.debug('No GOOGLE_OAUTH_CLIENT_SECRETS found; skipping interactive OAuth flow')
            except Exception:
                logging.debug('InstalledAppFlow unavailable or failed; ensure google-auth-oauthlib is installed')

        if creds is None:
            raise RuntimeError('Could not obtain Google Drive credentials via service account, ADC, or interactive OAuth.')

        # Build the Drive client
        self.service = build('drive', 'v3', credentials=creds)
        self.MediaFileUpload = MediaFileUpload
        self.MediaIoBaseDownload = MediaIoBaseDownload

    def _find_file(self, name: str):
        """Search for a file by name within the configured Drive folder.

        Returns the first matching file dict or None if not found.
        """
        try:
            # escape single quotes in the filename for the Drive query
            escaped = name.replace("'", "\\'")
            q = "name = '{}' and '{}' in parents and trashed = false".format(escaped, self.folder_id)
            res = self.service.files().list(q=q, fields='files(id,name)').execute()
            files = res.get('files', [])
            return files[0] if files else None
        except Exception:
            logging.exception('Error while searching for file on Google Drive')
            return None

    def upload_file(self, local_path: str):
        """Upload or update a single file to the configured Drive folder.

        Returns the Drive file id on success or None on failure.
        """
        name = os.path.basename(local_path)
        try:
            found = self._find_file(name)
            media = self.MediaFileUpload(local_path, resumable=True)
            if found:
                # update existing file
                res = self.service.files().update(fileId=found['id'], media_body=media).execute()
                fid = res.get('id') if isinstance(res, dict) else found.get('id')
                logging.info(f'Updated file on Drive: {name} (id={fid})')
                return fid
            else:
                file_metadata = {'name': name, 'parents': [self.folder_id]}
                res = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                fid = res.get('id') if isinstance(res, dict) else None
                logging.info(f'Uploaded file to Drive: {name} (id={fid})')
                return fid
        except Exception:
            logging.exception('Failed to upload/update file on Google Drive')
            return None

    def download_file(self, local_path: str):
        name = os.path.basename(local_path)
        found = self._find_file(name)
        if not found:
            logging.warning(f'No file named {name} found in Drive folder {self.folder_id}')
            return
        request = self.service.files().get_media(fileId=found['id'])
        fh = open(local_path, 'wb')
        downloader = self.MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.close()
        logging.info(f'Downloaded file from Drive: {name}')


class LocalDriveMemory:
    """Simple helper that copies files into a local Google Drive-mounted
    folder (for systems using Drive for Desktop or other mounts).

    This provides a low-friction alternative to the API when the Drive is
    available as a filesystem path (e.g. G:\My Drive\... on Windows).
    """

    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        if not os.path.exists(self.folder_path):
            try:
                os.makedirs(self.folder_path, exist_ok=True)
            except Exception:
                logging.exception('Could not create local Drive folder: %s', self.folder_path)
                raise

    def _target_path(self, name: str) -> str:
        return os.path.join(self.folder_path, name)

    def upload_file(self, local_path: str):
        """Copy the local file into the mounted Drive folder. Returns the
        destination path (as a string) on success or None on failure."""
        try:
            name = os.path.basename(local_path)
            dst = self._target_path(name)
            # Use binary copy
            with open(local_path, 'rb') as src_f, open(dst, 'wb') as dst_f:
                dst_f.write(src_f.read())
            logging.info('Copied memory file to local Drive folder: %s - memory.py:346', dst)
            return dst
        except Exception:
            logging.exception('Failed to copy file to local Drive folder')
            return None

    def download_file(self, local_path: str):
        # In a mounted scenario, the file should already be present; copy it back
        try:
            name = os.path.basename(local_path)
            src = self._target_path(name)
            if not os.path.exists(src):
                logging.warning('No file found in local Drive folder: %s - memory.py:358', src)
                return
            with open(src, 'rb') as src_f, open(local_path, 'wb') as dst_f:
                dst_f.write(src_f.read())
            logging.info('Copied memory file from local Drive folder: %s - memory.py:362', src)
        except Exception:
            logging.exception('Failed to download file from local Drive folder')
