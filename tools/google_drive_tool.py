"""Google Drive Integration Tool - Full Access"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import pickle
import io

SCOPES = ['https://www.googleapis.com/auth/drive']

class GoogleDriveTool:
    name = "google_drive"
    description = "Access Google Drive files with full permissions"
    
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive"""
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
    
    def list_folder(self, folder_id):
        """List all files in folder"""
        results = self.service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name, mimeType, size, modifiedTime)"
        ).execute()
        return results.get('files', [])
    
    def download_file(self, file_id, dest_path):
        """Download file from Drive"""
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(dest_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return dest_path
    
    def match(self, command: str) -> bool:
        return "google drive" in command.lower() or "gdrive" in command.lower()
    
    def execute(self, command: str, **kwargs) -> str:
        folder_id = "1Txp3oLLrfbsvYuN7rFnNhuKBTpdbXvfQ"
        files = self.list_folder(folder_id)
        return f"Found {len(files)} files: {[f['name'] for f in files]}"
