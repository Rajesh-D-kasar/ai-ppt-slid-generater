import os
import unittest
from io import BytesIO

from fastapi.testclient import TestClient
from pptx import Presentation

from app.main import app


VALID_PAYLOAD = {
    "topic": "AI tools for small businesses",
    "slide_count": 5,
    "audience": "small business owners",
    "tone": "professional",
    "theme": "modern",
    "language": "English",
    "include_speaker_notes": True,
    "extra_instructions": "Make it practical and easy to present.",
}


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        os.environ.pop("OPENAI_API_KEY", None)
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_theme_endpoint_lists_available_themes(self):
        response = self.client.get("/api/themes")

        self.assertEqual(response.status_code, 200)
        self.assertIn("modern", response.json()["themes"])
        self.assertIn("dark", response.json()["themes"])

    def test_preview_plan_returns_requested_slide_count(self):
        response = self.client.post("/api/preview-plan", json=VALID_PAYLOAD)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["title"], VALID_PAYLOAD["topic"])
        self.assertEqual(len(body["slides"]), VALID_PAYLOAD["slide_count"])
        self.assertTrue(body["slides"][0]["bullets"])

    def test_generate_ppt_returns_valid_powerpoint(self):
        response = self.client.post("/api/generate-ppt", json=VALID_PAYLOAD)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            response.headers["content-type"],
        )
        self.assertTrue(response.content.startswith(b"PK"))
        presentation = Presentation(BytesIO(response.content))
        self.assertEqual(len(presentation.slides), VALID_PAYLOAD["slide_count"] + 2)

    def test_invalid_slide_count_is_rejected(self):
        payload = {**VALID_PAYLOAD, "slide_count": 99}

        response = self.client.post("/api/preview-plan", json=payload)

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
