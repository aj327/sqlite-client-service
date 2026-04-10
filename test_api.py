import os
import tempfile
import unittest

from app import create_app
from models import Author, Book, db


class StatsEndpointTestCase(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        self.app = create_app(
            database_uri=f"sqlite:///{self.db_path}",
            enable_sentry=False,
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            author = Author(name="Jane Doe", bio="Test author")
            db.session.add(author)
            db.session.flush()
            db.session.add(Book(title="Old Book", year=1901, author_id=author.id))
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        os.unlink(self.db_path)

    def test_stats_returns_oldest_author_name(self):
        response = self.client.get("/api/stats")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "avg_books_per_author": 1.0,
                "oldest_author": "Jane Doe",
                "oldest_book": "Old Book",
                "oldest_year": 1901,
                "total_authors": 1,
                "total_books": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
