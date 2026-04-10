"""Populate the database with sample authors and books."""

from app import create_app
from models import db, Author, Book

AUTHORS_AND_BOOKS = [
    ("Gabriel García Márquez", "Colombian novelist", [
        ("One Hundred Years of Solitude", 1967),
        ("Love in the Time of Cholera", 1985),
        ("Chronicle of a Death Foretold", 1981),
    ]),
    ("Toni Morrison", "American novelist and Nobel laureate", [
        ("Beloved", 1987),
        ("Song of Solomon", 1977),
        ("The Bluest Eye", 1970),
        ("Sula", 1973),
    ]),
    ("Haruki Murakami", "Japanese writer", [
        ("Norwegian Wood", 1987),
        ("Kafka on the Shore", 2002),
        ("1Q84", 2009),
    ]),
    ("Chimamanda Ngozi Adichie", "Nigerian writer", [
        ("Half of a Yellow Sun", 2006),
        ("Americanah", 2013),
        ("Purple Hibiscus", 2003),
    ]),
    ("Jorge Luis Borges", "Argentine writer", [
        ("Ficciones", 1944),
        ("The Aleph", 1949),
        ("Labyrinths", 1962),
    ]),
    ("Virginia Woolf", "English modernist author", [
        ("Mrs Dalloway", 1925),
        ("To the Lighthouse", 1927),
        ("Orlando", 1928),
        ("The Waves", 1931),
    ]),
    ("Fyodor Dostoevsky", "Russian novelist", [
        ("Crime and Punishment", 1866),
        ("The Brothers Karamazov", 1880),
        ("The Idiot", 1869),
        ("Notes from Underground", 1864),
    ]),
    ("Isabel Allende", "Chilean writer", [
        ("The House of the Spirits", 1982),
        ("Eva Luna", 1987),
        ("City of the Beasts", 2002),
    ]),
    ("Franz Kafka", "Czech-born writer", [
        ("The Trial", 1925),
        ("The Metamorphosis", 1915),
        ("The Castle", 1926),
    ]),
    ("Ursula K. Le Guin", "American author", [
        ("The Left Hand of Darkness", 1969),
        ("A Wizard of Earthsea", 1968),
        ("The Dispossessed", 1974),
        ("The Lathe of Heaven", 1971),
    ]),
]


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        for author_name, bio, books in AUTHORS_AND_BOOKS:
            author = Author(name=author_name, bio=bio)
            db.session.add(author)
            db.session.flush()

            for title, year in books:
                db.session.add(Book(title=title, year=year, author_id=author.id))

        db.session.commit()
        print(f"Seeded {len(AUTHORS_AND_BOOKS)} authors with their books.")


if __name__ == "__main__":
    seed()
