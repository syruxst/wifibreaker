"""Unit tests for scanner module."""

import unittest
from core.scanner import WiFiNetwork


class TestScanner(unittest.TestCase):
    """Test network scanner."""
    
    def test_network_creation(self):
        """Test WiFiNetwork object."""
        network = WiFiNetwork(
            bssid="AA:BB:CC:DD:EE:FF",
            ssid="TestNetwork",
            channel=6,
            signal=-50,
            encryption="WPA2"
        )
        
        self.assertEqual(network.ssid, "TestNetwork")
        self.assertEqual(network.channel, 6)


if __name__ == '__main__':
    unittest.main()