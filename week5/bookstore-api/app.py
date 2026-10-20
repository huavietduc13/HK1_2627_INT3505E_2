from flask import Flask
from models import db
from routes.authors import authors_bp
from routes.books import books_bp
from routes.categories import categories_bp

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(books_bp)
app.register_blueprint(authors_bp)
app.register_blueprint(categories_bp)

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)