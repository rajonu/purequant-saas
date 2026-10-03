import http.client
import json
import pathlib
import threading
import unittest
from http.server import HTTPServer


ROOT = pathlib.Path(__file__).resolve().parent


class StaticHardeningTests(unittest.TestCase):
    def test_vercel_deployment_excludes_runtime_material(self):
        rules = (ROOT / ".vercelignore").read_text(encoding="utf-8")
        for required in ("*.py", "*.map", ".env*", "data/", "Dockerfile", "Procfile"):
            self.assertIn(required, rules)

    def test_vercel_has_baseline_security_headers(self):
        config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
        all_headers = {
            header["key"]: header["value"]
            for rule in config["headers"]
            for header in rule["headers"]
        }
        self.assertEqual(all_headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(all_headers["Strict-Transport-Security"], "max-age=31536000")
        self.assertIn("camera=()", all_headers["Permissions-Policy"])

    def test_sensitive_static_pages_are_not_indexable(self):
        files = (
            "health.html",
            "health/index.html",
            "status.html",
            "status/index.html",
            "landing_page/health.html",
            "landing_page/health/index.html",
            "landing_page/status.html",
            "landing_page/status/index.html",
        )
        for relative in files:
            html = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(
                '<meta name="robots" content="noindex, nofollow, noarchive">',
                html,
                relative,
            )

    def test_status_dashboard_has_no_embedded_telegram_bot_url(self):
        html = (ROOT / "landing_page/status/index.html").read_text(encoding="utf-8")
        self.assertNotRegex(html, r"api\.telegram\.org/bot\d+:")


class HealthResponseTests(unittest.TestCase):
    def test_health_response_is_cache_safe_and_does_not_fingerprint_python(self):
        from subscription_bot import HealthCheckHandler

        server = HTTPServer(("127.0.0.1", 0), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request("GET", "/health")
            response = connection.getresponse()
            body = response.read()
            self.assertEqual(response.status, 200)
            self.assertEqual(body, b"PureQuant AI Paywall Bot is Active & Running 24/7 OK")
            self.assertEqual(response.getheader("Cache-Control"), "no-store")
            self.assertEqual(response.getheader("X-Content-Type-Options"), "nosniff")
            self.assertEqual(response.getheader("Server"), "PureQuant-Health")
            self.assertNotIn("Python", response.getheader("Server", ""))
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
