from strats.settings import STRAVA_ACCESS_TOKEN, STRAVA_REFRESH_TOKEN
from stravalib.client import Client


def create_strava_client():
    client = Client()
    client.access_token = STRAVA_ACCESS_TOKEN
    client.refresh_token = STRAVA_REFRESH_TOKEN
    return client
