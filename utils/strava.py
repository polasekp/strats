import logging

from stravalib.client import Client

import my_secrets

logger = logging.getLogger(__name__)


class StravaHelper:
    def __init__(self):
        self._token = None
        self._client = None

    @staticmethod
    def print_authorization_url():
        """to get the STRAVA_CODE you need to manually confirm following request"""
        print(f"https://www.strava.com/oauth/authorize?client_id={my_secrets.STRAVA_CLIENT_ID}&redirect_uri=http://localhost&approval_prompt=auto&response_type=code&scope=profile:read_all,activity:read_all")

    def _get_strava_token(self):
        from activities.models import StravaToken

        token = StravaToken.objects.first()
        if not token:
            logger.info("Creating new Strava token")
            token_response = self._client.exchange_code_for_token(
                client_id=my_secrets.STRAVA_CLIENT_ID, client_secret=my_secrets.STRAVA_CLIENT_SECRET, code=my_secrets.STRAVA_CODE
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
            self._client = self._init_client()
        if self.token.is_expired:
            self._refresh_client()
        return self._client

    def _refresh_client(self):
        logger.info("Refreshing strava client")
        refresh_response = self._client.refresh_access_token(
            client_id=my_secrets.STRAVA_CLIENT_ID, client_secret=my_secrets.STRAVA_CLIENT_SECRET, refresh_token=self.token.refresh_token
        )
        self.token.access_token = refresh_response["access_token"]
        self.token.refresh_token = refresh_response["refresh_token"]
        self.token.expires_at = refresh_response["expires_at"]
        self._client.access_token = refresh_response["access_token"]
        self.token.save()

    def _init_client(self):
        logger.info("Obtaining new strava client")
        client = Client()
        client.access_token = self.token.access_token
        return client
