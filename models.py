from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, default="")

    books = db.relationship("Book", back_populates="author", lazy="select")

    def to_dict(self, include_books=True):
        data = {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
        }
        if include_books:
            data["books"] = [book.to_dict() for book in self.books]
        return data


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    author = db.relationship("Author", back_populates="books")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
        }
