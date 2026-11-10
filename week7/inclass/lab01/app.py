import os
from flask import Flask
from extensions import db
from errors import register_error_handlers
from products import products_bp
from orders import orders_bp
from health import health_bp

def create_app():
    app = Flask(__name__)
    
    # Đọc cấu hình từ biến môi trường DB_URL (dùng cho Docker/PostgreSQL), mặc định là SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL", "sqlite:///dev.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    register_error_handlers(app)

    # Đăng ký các Blueprint
    app.register_blueprint(health_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
