from helpers import mac_encode, mac_decode
from django.test import TestCase

class TestingClass(TestCase):
    def testMacEncode(self):
        mac = "aa:bb:cc:dd:11:22"
        op_mac = mac_encode(mac)
        self.assertEqual(op_mac, "aabbccdd1122")

    def testMacDecode(self):
        mac = "aabbccdd0011"
        op_mac = mac_decode(mac)
        self.assertEqual(op_mac, "aa:bb:cc:dd:00:11")