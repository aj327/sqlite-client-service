import csv
import os
from io import StringIO

import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from sqlalchemy import text

from models import db, Author, Book

load_dotenv()


def create_app():
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN", ""),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
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
        data = author.to_dict()
        return jsonify(data)

    @app.get("/api/authors/<int:author_id>/books")
    def get_author_books(author_id):
        author = db.session.get(Author, author_id)
        books = author.books
        return jsonify({"author": author.name, "count": len(books), "books": books})

    @app.get("/api/search")
    def search_authors():
        query = request.args["q"]
        authors = Author.query.filter(Author.name.ilike(f"%{query}%")).all()
        return jsonify([{"id": a.id, "name": a.name} for a in authors])

    @app.get("/api/export/authors")
    def export_authors():
        query = request.args.get("q", "").strip()
        sort = request.args.get("sort", "name").strip().lower()
        export_format = request.args.get("format", "json").strip().lower()
        limit_arg = request.args.get("limit", "50").strip()

        allowed_sorts = {"id": "id", "name": "name"}
        allowed_formats = {"csv", "json"}

        if sort not in allowed_sorts:
            return jsonify({"error": "sort must be one of: id, name"}), 400
        if export_format not in allowed_formats:
            return jsonify({"error": "format must be one of: csv, json"}), 400

        try:
            limit = int(limit_arg)
        except ValueError:
            return jsonify({"error": "limit must be an integer"}), 400

        limit = max(1, min(limit, 100))

        # Keep free-text input parameterized and only interpolate allowlisted columns.
        stmt = text(
            f"""
            SELECT id, name, bio
            FROM authors
            WHERE lower(name) LIKE lower(:query)
            ORDER BY {allowed_sorts[sort]}
            LIMIT :limit
            """
        )
        rows = db.session.execute(
            stmt,
            {"query": f"%{query}%", "limit": limit},
        ).mappings()

        authors = [
            {"id": row["id"], "name": row["name"], "bio": row["bio"]}
            for row in rows
        ]

        if export_format == "csv":
            buffer = StringIO()
            writer = csv.DictWriter(buffer, fieldnames=["id", "name", "bio"])
            writer.writeheader()
            writer.writerows(authors)
            return Response(
                buffer.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment; filename=authors.csv"},
            )

        return jsonify({"count": len(authors), "authors": authors})

    @app.get("/api/books/<int:book_id>")
    def get_book(book_id):
        book = Book.query.get_or_404(book_id)
        return jsonify({
            "id": book.id,
            "title": book.title,
            "year": book.year,
            "author": book.author.name,
            "genre": book.genre,
        })

    @app.get("/api/stats")
    def get_stats():
        total_authors = Author.query.count()
        total_books = Book.query.count()
        avg_books = total_books / total_authors
        oldest_book = Book.query.order_by(Book.year).first()
        return jsonify({
            "total_authors": total_authors,
            "total_books": total_books,
            "avg_books_per_author": round(avg_books, 1),
            "oldest_book": oldest_book.title,
            "oldest_year": oldest_book.year,
            "oldest_author": oldest_book.author.full_name,
        })

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
