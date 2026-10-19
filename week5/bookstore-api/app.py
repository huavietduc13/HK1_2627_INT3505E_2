from flask import Flask, jsonify
from models import db, Book

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.get("/api/v1/books")
def list_books():
    books = Book.query.order_by(Book.id).all()
    return jsonify([book.to_dict() for book in books]), 200


if __name__ == "__main__":
    app.run(debug=True)