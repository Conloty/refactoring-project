from flask import Flask
from flask_cors import CORS
from db import db
from routes import init_routes

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/Practice_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    init_routes(app)

    return app

app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



