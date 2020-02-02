import requests
from stravalib.client import Client

from strats.settings import CLIENT_ID, CLIENT_SECRET, STRAVA_CODE

# to get the STRAVA_CODE you need to manually confirm following request
# https://www.strava.com/oauth/authorize?
#     client_id=33679&
#     redirect_uri=http://localhost&
#     response_type=code&
#     scope=profile:read_all,activity:read_all


def get_access_and_refresh_token():
    url = f"https://www.strava.com/oauth/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}" \
          f"&code={STRAVA_CODE}&grant_type=authorization_code"
    response_data = requests.post(url).json()
    return response_data.get("access_token"), response_data.get("refresh_token")


def get_strava_client():
    access_token, _ = get_access_and_refresh_token()
    # print(access_token)
    # access_token = "7cf50f65a27fa9263147f8b1c3608707235fd198"
    client = Client(access_token=access_token)
    return client
