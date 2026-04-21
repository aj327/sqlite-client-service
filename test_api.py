import unittest

from app import create_app
from models import db, Author


class AuthorEndpointTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(database_uri="sqlite:///:memory:", enable_sentry=False)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            db.session.add(Author(name="Test Author", bio="Bio"))
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_author_returns_serialized_author(self):
        response = self.client.get("/api/authors/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"id": 1, "name": "Test Author", "bio": "Bio"},
        )

    def test_get_author_returns_404_for_missing_author(self):
        response = self.client.get("/api/authors/99999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Author not found"})


if __name__ == "__main__":
    unittest.main()
