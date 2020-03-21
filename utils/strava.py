import logging

from stravalib.client import Client

import secrets
from activities.models import StravaToken
from utils.models import create_or_update_activity_from_strava

logger = logging.getLogger(__name__)


class StravaHelper:
    def __init__(self):
        self._token = None
        self._client = None

    @staticmethod
    def print_authorization_url():
        """to get the STRAVA_CODE you need to manually confirm following request"""
        print(f"https://www.strava.com/oauth/authorize?client_id={secrets.STRAVA_CLIENT_ID}&redirect_uri=http://localhost&approval_prompt=auto&response_type=code&scope=profile:read_all,activity:read_all")

    def _get_strava_token(self):
        token = StravaToken.objects.first()
        if not token:
            logger.info("Creating new Strava token")
            token_response = self._client.exchange_code_for_token(
                client_id=secrets.STRAVA_CLIENT_ID, client_secret=secrets.STRAVA_CLIENT_SECRET, code=secrets.STRAVA_CODE
            )
            token = StravaToken.objects.create(
                access_token=token_response["access_token"],
                refresh_token=token_response["refresh_token"],
                expires_at=token_response["expires_at"],
            )
        return token

    @property
    def token(self):
        if not self._token:
            self._token = self._get_strava_token()
        return self._token

    @property
    def client(self):
        if not self._client:
            self._init_client()
        if self.token.is_expired:
            self._refresh_client()
        return self._client

    def _refresh_client(self):
        logger.info("Refreshing strava client")
        refresh_response = self.client.refresh_access_token(
            client_id=secrets.STRAVA_CLIENT_ID, client_secret=secrets.STRAVA_CLIENT_SECRET, refresh_token=self.token.refresh_token
        )
        self.token.access_token = refresh_response["access_token"]
        self.token.refresh_token = refresh_response["refresh_token"]
        self.token.expires_at = refresh_response["expires_at"]
        self.client.access_token = refresh_response["access_token"]
        self.token.save()

    def _init_client(self):
        logger.info("Obtaining new strava client")
        self._client = Client()
        self._client.access_token = self.token.access_token

    def refresh_activity(self, activity):
        logger.info(f"Refreshing activity {activity.strava_id} from Strava")
        strava_activity = self.client.get_activity(activity.strava_id)
        create_or_update_activity_from_strava(strava_activity)
