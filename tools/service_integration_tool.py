"""
Service Integration Tool for ULTRON Agent

Provides integration with external services like Google Calendar, email, and more
"""

import logging
import os
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import urllib.parse

# ULTRON Agent imports
from utils.ultron_logger import log_info, log_error, log_ai_decision

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    log_error("service_integration", "Google API client not available. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class ServiceIntegrationTool:
    """
    Tool for integrating with external services
    """

    name = "Service Integration Tool"
    description = "Integrate with external services like Google Calendar, email, and web APIs"

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
              'https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.send']

    def __init__(self):
        self.google_creds = None
        self.calendar_service = None
        self.gmail_service = None
        self.email_config = {}
        self._load_config()

    def _load_config(self):
        """Load service integration configuration"""
        try:
            config_path = Path("ultron_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)

                # Load email configuration
                self.email_config = config.get('service_integration', {}).get('email', {})

                # Load Google API credentials path
                google_creds_path = config.get('service_integration', {}).get('google_credentials_path')
                if google_creds_path and Path(google_creds_path).exists():
                    self._setup_google_services(google_creds_path)

        except Exception as e:
            log_error("service_integration", f"Config loading failed: {e}")

    def _setup_google_services(self, credentials_path: str):
        """Setup Google API services"""
        if not GOOGLE_API_AVAILABLE:
            return

        try:
            creds = None
            token_path = Path("token.json")

            # Load existing token if available
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)

            # Refresh or create new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save credentials
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            # Build services
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.google_creds = creds

            log_info("service_integration", "Google services initialized")

        except Exception as e:
            log_error("service_integration", f"Google services setup failed: {e}")

    def match(self, command: str) -> bool:
        """Check if command matches service integration operations"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            "google calendar", "check calendar", "email", "send email", "read email",
            "calendar events", "schedule", "gmail", "service integration", "api call"
        ])

    def execute(self, command: str) -> str:
        """Execute service integration operations"""
        try:
            command_lower = command.lower()

            if "calendar" in command_lower or "schedule" in command_lower:
                if "google" in command_lower:
                    return self.get_google_calendar_events()
                else:
                    return "Calendar integration requires Google Calendar setup"
            elif "email" in command_lower:
                if "send" in command_lower:
                    return self.send_email_via_smtp(command)
                elif "read" in command_lower or "check" in command_lower:
                    return self.read_recent_emails()
                else:
                    return "Specify 'send email' or 'read email'"
            elif "api" in command_lower:
                return self.make_api_call(command)
            else:
                return self.get_help()

        except Exception as e:
            log_error("service_integration", f"Service operation failed: {e}")
            return f"Service operation failed: {str(e)}"

    def get_google_calendar_events(self) -> str:
        """Get upcoming Google Calendar events"""
        if not self.calendar_service:
            return """
❌ **Google Calendar Not Available**

**Setup Required:**
1. Enable Google Calendar API in Google Cloud Console
2. Download credentials.json
3. Add to ultron_config.json:
```json
{
  "service_integration": {
    "google_credentials_path": "path/to/credentials.json"
  }
}
```
4. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

**Command:** pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

        try:
            log_info("service_integration", "Fetching Google Calendar events")

            # Get upcoming events
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            if not events:
                return "📅 **No upcoming events found**"

            result = f"""
📅 **Upcoming Google Calendar Events** ({len(events)} found)

"""

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_time = self._parse_datetime(start)

                result += f"""
**{event['summary']}**
• Time: {start_time}
• Calendar: {event.get('organizer', {}).get('displayName', 'Primary')}
"""

                if 'location' in event:
                    result += f"• Location: {event['location']}\n"
                if 'description' in event:
                    desc = event['description'][:100] + "..." if len(event['description']) > 100 else event['description']
                    result += f"• Description: {desc}\n"

            return result

        except Exception as e:
            log_error("service_integration", f"Calendar fetch failed: {e}")
            return f"Failed to fetch calendar events: {str(e)}"

    def send_email_via_smtp(self, command: str) -> str:
        """Send email via SMTP"""
        try:
            # Parse command for email details
            # Expected format: send email to:recipient@domain.com subject:"Subject" body:"Message"
            import re

            to_match = re.search(r'to:([^\s]+)', command)
            subject_match = re.search(r'subject:"([^"]*)"', command)
            body_match = re.search(r'body:"([^"]*)"', command)

            if not all([to_match, subject_match, body_match]):
                return """
❌ **Invalid Email Format**

**Correct Format:**
send email to:recipient@domain.com subject:"Your Subject" body:"Your message here"

**Example:**
send email to:user@example.com subject:"Hello from ULTRON" body:"This is a test message"
"""

            to_email = to_match.group(1)
            subject = subject_match.group(1)
            body = body_match.group(1)

            # Check SMTP configuration
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            smtp_user = self.email_config.get('smtp_user')
            smtp_password = self.email_config.get('smtp_password')

            if not all([smtp_user, smtp_password]):
                return """
❌ **SMTP Configuration Required**

Add to ultron_config.json:
```json
{
  "service_integration": {
    "email": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "smtp_user": "your-email@gmail.com",
      "smtp_password": "your-app-password"
    }
  }
}
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate App Password: https://support.google.com/accounts/answer/185833
3. Use App Password (not regular password)
"""

            # Send email
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_user, to_email, text)
            server.quit()

            log_info("service_integration", f"Email sent to {to_email}")
            return f"""
✅ **Email Sent Successfully**

**To:** {to_email}
**Subject:** {subject}
**Body:** {body[:100]}...
"""

        except Exception as e:
            log_error("service_integration", f"Email send failed: {e}")
            return f"Failed to send email: {str(e)}"

    def read_recent_emails(self) -> str:
        """Read recent emails"""
        if not self.gmail_service:
            return """
❌ **Gmail Integration Not Available**

**Setup Required:**
1. Enable Gmail API in Google Cloud Console
2. Download credentials.json
3. Configure in ultron_config.json
4. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

        try:
            log_info("service_integration", "Fetching recent emails")

            # Get recent messages
            results = self.gmail_service.users().messages().list(
                userId='me',
                maxResults=5
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return "📧 **No emails found**"

            result = f"""
📧 **Recent Gmail Messages** ({len(messages)} found)

"""

            for msg in messages:
                msg_data = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()

                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

                # Get snippet
                snippet = msg_data.get('snippet', 'No preview available')

                result += f"""
**{subject}**
• From: {sender}
• Date: {date}
• Preview: {snippet[:100]}...
"""

            return result

        except Exception as e:
            log_error("service_integration", f"Email read failed: {e}")
            return f"Failed to read emails: {str(e)}"

    def make_api_call(self, command: str) -> str:
        """Make a generic API call"""
        if not REQUESTS_AVAILABLE:
            return "❌ Requests library not available. Install with: pip install requests"

        try:
            # Parse API call from command
            # Expected format: api call GET https://api.example.com/endpoint
            import re

            api_match = re.search(r'(GET|POST|PUT|DELETE)\s+(https?://[^\s]+)', command, re.IGNORECASE)
            if not api_match:
                return """
❌ **Invalid API Call Format**

**Correct Format:**
api call GET https://api.example.com/endpoint
api call POST https://api.example.com/endpoint data:{"key": "value"}

**Examples:**
api call GET https://api.github.com/user
api call GET https://httpbin.org/json
"""

            method = api_match.group(1).upper()
            url = api_match.group(2)

            # Check for data payload
            data_match = re.search(r'data:(\{.*\})', command)
            data = None
            if data_match:
                try:
                    data = json.loads(data_match.group(1))
                except:
                    return "❌ Invalid JSON data format"

            log_info("service_integration", f"Making API call: {method} {url}")

            # Make the request
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=10)
            else:
                return f"❌ Unsupported HTTP method: {method}"

            result = f"""
🌐 **API Call Result**

**Request:** {method} {url}
**Status:** {response.status_code} {response.reason}

**Response Headers:**
{chr(10).join(f"• {k}: {v}" for k, v in response.headers.items() if k.lower() in ['content-type', 'server', 'date'])}

**Response Body:**
"""

            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    json_data = response.json()
                    result += json.dumps(json_data, indent=2)
                else:
                    result += response.text[:1000]  # Limit output
                    if len(response.text) > 1000:
                        result += "\n\n... (truncated)"
            except:
                result += response.text[:1000]
                if len(response.text) > 1000:
                    result += "\n\n... (truncated)"

            return result

        except requests.exceptions.RequestException as e:
            log_error("service_integration", f"API call failed: {e}")
            return f"API call failed: {str(e)}"
        except Exception as e:
            log_error("service_integration", f"API call error: {e}")
            return f"API call error: {str(e)}"

    def _parse_datetime(self, dt_str: str) -> str:
        """Parse datetime string for display"""
        try:
            if 'T' in dt_str:
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(dt_str, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return dt_str

    def get_help(self) -> str:
        """Get help information for the tool"""
        google_status = "✅ Available" if self.calendar_service else "❌ Not Configured"
        email_status = "✅ Available" if self.email_config.get('smtp_user') else "❌ Not Configured"

        return """
🔗 **Service Integration Tool**

**Available Integrations:**
• Google Calendar: """ + google_status + """
• Email (SMTP): """ + email_status + """
• Generic API Calls: ✅ Available

**Commands:**

**Google Calendar:**
• "check google calendar" - Get upcoming events

**Email:**
• "send email to:user@domain.com subject:\"Subject\" body:\"Message\"" - Send email
• "read recent emails" - Check Gmail inbox

**API Calls:**
• "api call GET https://api.example.com" - Make HTTP request
• "api call POST https://api.example.com data:{\"key\":\"value\"}" - POST with JSON data

**Setup Instructions:**

**Google Services:**
1. Create Google Cloud Project
2. Enable Calendar API and Gmail API
3. Create OAuth 2.0 credentials
4. Download credentials.json
5. Add to ultron_config.json:
```json
{
  "service_integration": {
    "google_credentials_path": "credentials.json"
  }
}
```

**Email (SMTP):**
Add to ultron_config.json:
```json
{
  "service_integration": {
    "email": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "smtp_user": "your-email@gmail.com",
      "smtp_password": "your-app-password"
    }
  }
}
```

**Requirements:**
• Google APIs: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
• Requests: pip install requests
"""

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Service integration command"
                    }
                },
                "required": ["command"]
            }
        }
