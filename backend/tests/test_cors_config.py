import re
import unittest

from app.core.config import settings
from app.main import _local_dev_origin_regex


class CorsConfigTest(unittest.TestCase):
    def setUp(self):
        self._frontend_url = settings.FRONTEND_URL

    def tearDown(self):
        settings.FRONTEND_URL = self._frontend_url

    def test_local_dev_regex_allows_loopback_and_private_mobile_hosts(self):
        settings.FRONTEND_URL = "http://localhost:3000"
        pattern = re.compile(_local_dev_origin_regex() or "")

        self.assertRegex("http://127.0.0.1:3000", pattern)
        self.assertRegex("http://192.168.1.25:3000", pattern)

    def test_local_dev_regex_is_disabled_for_production_frontend(self):
        settings.FRONTEND_URL = "https://ai-trainer.ru"

        self.assertIsNone(_local_dev_origin_regex())


if __name__ == "__main__":
    unittest.main()
