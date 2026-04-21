import unittest

from app import create_app
from models import Author, Book, db


class AuthorDetailsApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(database_uri="sqlite:///:memory:", enable_sentry=False)
        self.app.config["TESTING"] = True

        with self.app.app_context():
            db.create_all()
            author = Author(name="Test Author", bio="Test Bio")
            db.session.add(author)
            db.session.flush()
            db.session.add(Book(title="Test Book", year=2024, author_id=author.id))
            db.session.commit()
            self.author_id = author.id

        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_author_details_returns_serialized_author(self):
        response = self.client.get(f"/api/authors/{self.author_id}")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["id"], self.author_id)
        self.assertEqual(payload["name"], "Test Author")
        self.assertEqual(payload["bio"], "Test Bio")
        self.assertEqual(len(payload["books"]), 1)
        self.assertEqual(payload["books"][0]["title"], "Test Book")
        self.assertEqual(payload["books"][0]["year"], 2024)

    def test_author_details_returns_404_for_missing_author(self):
        response = self.client.get("/api/authors/9999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
