from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

db = SQLAlchemy()

book_authors = db.Table(
    "book_authors",
    db.Column("book_id", Integer, ForeignKey("book.id"), primary_key=True),
    db.Column("author_id", Integer, ForeignKey("author.id"), primary_key=True),
)


class Book(db.Model):
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(200), nullable=False)
    isbn = mapped_column(String(13), unique=True, nullable=False)
    price_vnd = mapped_column(Integer, nullable=False)
    stock = mapped_column(Integer, default=0, nullable=False)
    category_id = mapped_column(ForeignKey("category.id"), nullable=False)

    category = relationship("Category")
    authors = relationship("Author", secondary=book_authors)

    def to_dict(self):
        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category_id": self.category_id,
            "authors": [author.to_dict() for author in self.authors],
        }


class Author(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    bio = mapped_column(Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
        }


class Category(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    slug = mapped_column(String(100), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
        }


class User(db.Model):
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(255), unique=True, nullable=False)
    display_name = mapped_column(String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
        }


class Review(db.Model):
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_1_to_5"),
    )

    id = mapped_column(Integer, primary_key=True)
    rating = mapped_column(Integer, nullable=False)
    book_id = mapped_column(ForeignKey("book.id"), nullable=False)
    user_id = mapped_column(ForeignKey("user.id"), nullable=False)

    book = relationship("Book")
    user = relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "book_id": self.book_id,
            "user_id": self.user_id,
        }
