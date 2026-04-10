import os

import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, jsonify

from models import db, Author

load_dotenv()


def create_app(database_uri=None, enable_sentry=True):
    if enable_sentry:
        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN", ""),
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri or "sqlite:///library.db"
    db.init_app(app)

    @app.get("/api/authors")
    def list_authors_with_books():
        """N+1 query: fetches every author, then issues a separate query
        per author to load their books."""
        authors = Author.query.all()

        result = []
        for author in authors:
            result.append({
                "id": author.id,
                "name": author.name,
                "bio": author.bio,
                "books": [
                    {"id": b.id, "title": b.title, "year": b.year}
                    for b in author.books   # triggers a SELECT per author
                ],
            })
        return jsonify(result)

    @app.get("/api/authors/<int:author_id>")
    def get_author(author_id):
        author = db.session.get(Author, author_id)
        if author is None:
            return jsonify({"error": "Author not found"}), 404
        return jsonify(author.to_dict(include_books=True))

    @app.get("/api/authors/<int:author_id>/books")
    def get_author_books(author_id):
        author = db.session.get(Author, author_id)
        if author is None:
            return jsonify({"error": "Author not found"}), 404

        books = [book.to_dict() for book in author.books]
        return jsonify({"author": author.name, "count": len(books), "books": books})

    @app.get("/debug-sentry")
    def trigger_error():
        division_by_zero = 1 / 0

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5001)
