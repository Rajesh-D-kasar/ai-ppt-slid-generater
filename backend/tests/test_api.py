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
    "deck_type": "business",
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


    def test_ai_status_endpoint_reports_demo_mode(self):
        response = self.client.get("/api/ai-status")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["mode"], "demo")
        self.assertFalse(body["has_api_key"])
        self.assertEqual(body["model"], "gpt-4.1-mini")

    def test_ai_status_endpoint_reports_openai_mode(self):
        os.environ["OPENAI_API_KEY"] = "test-key"
        self.addCleanup(lambda: os.environ.pop("OPENAI_API_KEY", None))

        response = self.client.get("/api/ai-status")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["mode"], "openai")
        self.assertTrue(body["has_api_key"])

    def test_theme_endpoint_lists_available_themes(self):
        response = self.client.get("/api/themes")

        self.assertEqual(response.status_code, 200)
        self.assertIn("modern", response.json()["themes"])
        self.assertIn("dark", response.json()["themes"])

    def test_deck_type_endpoint_lists_available_templates(self):
        response = self.client.get("/api/deck-types")

        self.assertEqual(response.status_code, 200)
        deck_types = response.json()["deck_types"]
        self.assertEqual(deck_types["business"], "Business Brief")
        self.assertIn("startup_pitch", deck_types)

    def test_preview_plan_returns_requested_slide_count_and_layouts(self):
        response = self.client.post("/api/preview-plan", json=VALID_PAYLOAD)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["title"], VALID_PAYLOAD["topic"])
        self.assertEqual(len(body["slides"]), VALID_PAYLOAD["slide_count"])
        self.assertTrue(body["slides"][0]["bullets"])
        self.assertIn(body["slides"][0]["layout"], {"bullets", "two_column", "timeline", "metrics", "quote", "closing"})
        self.assertEqual(body["slides"][-1]["layout"], "closing")

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

    def test_pitch_deck_uses_pitch_specific_structure(self):
        payload = {**VALID_PAYLOAD, "deck_type": "startup_pitch", "theme": "startup"}

        response = self.client.post("/api/preview-plan", json=payload)

        self.assertEqual(response.status_code, 200)
        titles = [slide["title"] for slide in response.json()["slides"]]
        self.assertIn("Problem", titles)
        self.assertIn("The Ask", titles)

    def test_invalid_slide_count_is_rejected(self):
        payload = {**VALID_PAYLOAD, "slide_count": 99}

        response = self.client.post("/api/preview-plan", json=payload)

        self.assertEqual(response.status_code, 422)

    def test_invalid_deck_type_is_rejected(self):
        payload = {**VALID_PAYLOAD, "deck_type": "unknown"}

        response = self.client.post("/api/preview-plan", json=payload)

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()