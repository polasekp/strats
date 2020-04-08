import logging
import os

from django.conf import settings
from garminconnect import Garmin

import my_secrets

logger = logging.getLogger(__name__)


class GarminHelper:
    def __init__(self):
        self._client = None

    @staticmethod
    def _get_client():
        logger.info("Obtaining garmin client")
        client = Garmin(my_secrets.GARMIN_EMAIL, my_secrets.GARMIN_PASSWORD)
        client.login()
        return client

    @property
    def client(self):
        if not self._client:
            self._client = self._get_client()
        return self._client

    def _get_request(self, url):
        return self.client.req.get(url, headers=self.client.headers)

    def download_activity(self, garmin_id):
        output_name = f"{garmin_id}.zip"
        output_path = os.path.join(settings.GARMIN_DOWNLOAD_DIR, output_name)
        if os.path.exists(output_path):
            logger.warning(f"Activity {garmin_id} already exists, skipping")
            return

        logger.info(f"Downloading garmin activity {garmin_id}")
        url = f"https://connect.garmin.com/modern/proxy/download-service/files/activity/{garmin_id}"
        response = self._get_request(url)
        with open(output_path, "wb") as download_file:
            download_file.write(response.content)
