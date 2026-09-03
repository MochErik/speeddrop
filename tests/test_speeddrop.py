"""Unit tests for SpeedDrop."""

import unittest
from speeddrop.lan_ip import get_local_lan_ip


class TestSpeedDrop(unittest.TestCase):

    def test_local_ip_discovery(self):
        ip = get_local_lan_ip()
        self.assertIsInstance(ip, str)
        self.assertGreater(len(ip), 6)


if __name__ == "__main__":
    unittest.main()
