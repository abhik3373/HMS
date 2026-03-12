import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

CREDENTIALS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'credentials.json'
)


def get_flow():
    return Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )


def credentials_from_token(token_dict):
    return Credentials(
        token=token_dict.get('token'),
        refresh_token=token_dict.get('refresh_token'),
        token_uri=token_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )


def get_calendar_service(token_dict):
    creds = credentials_from_token(token_dict)
    return build('calendar', 'v3', credentials=creds)
