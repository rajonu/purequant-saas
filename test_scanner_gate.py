import os
import unittest

os.environ["SCANNER_GATE_SECRET"] = "test-secret-for-scanner-gate-32-chars"

from scanner_gate import issue_token, verify_token


class ScannerGateTests(unittest.TestCase):
    def test_round_trip(self):
        token = issue_token(12345, now=1000)
        self.assertEqual(verify_token(token, now=1001)["uid"], 12345)

    def test_expired(self):
        token = issue_token(12345, ttl_seconds=10, now=1000)
        self.assertIsNone(verify_token(token, now=1010))

    def test_tampered(self):
        token = issue_token(12345, now=1000)
        body, sig = token.split(".", 1)
        self.assertIsNone(verify_token(body + "x." + sig, now=1001))


if __name__ == "__main__":
    unittest.main()
