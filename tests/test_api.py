import os
import tempfile
import unittest

from app import create_app
from models import Author, Book, db


class AuthorEndpointSerializationTests(unittest.TestCase):
    def setUp(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        self._db_fd = fd
        self._db_path = path
        self.app = create_app(
            database_uri=f"sqlite:///{self._db_path}",
            enable_sentry=False,
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            author = Author(name="Test Author", bio="Test bio")
            db.session.add(author)
            db.session.flush()
            db.session.add(Book(title="Book One", year=2001, author_id=author.id))
            db.session.add(Book(title="Book Two", year=2002, author_id=author.id))
            db.session.commit()
            self.author_id = author.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def test_get_author_serializes_author_and_books(self):
        response = self.client.get(f"/api/authors/{self.author_id}")
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertEqual(payload["id"], self.author_id)
        self.assertEqual(payload["name"], "Test Author")
        self.assertIsInstance(payload["books"], list)
        self.assertEqual(len(payload["books"]), 2)
        for book in payload["books"]:
            self.assertEqual(
                set(book.keys()),
                {"id", "title", "year", "author_id"},
            )

    def test_get_author_books_serializes_books(self):
        response = self.client.get(f"/api/authors/{self.author_id}/books")
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertEqual(payload["author"], "Test Author")
        self.assertEqual(payload["count"], 2)
        self.assertIsInstance(payload["books"], list)
        self.assertEqual(len(payload["books"]), 2)
        for book in payload["books"]:
            self.assertIsInstance(book, dict)
            self.assertEqual(
                set(book.keys()),
                {"id", "title", "year", "author_id"},
            )

    def test_get_author_returns_404_for_missing_author(self):
        response = self.client.get("/api/authors/999999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Author not found"})

    def test_get_author_books_returns_404_for_missing_author(self):
        response = self.client.get("/api/authors/999999/books")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Author not found"})


if __name__ == "__main__":
    unittest.main()
