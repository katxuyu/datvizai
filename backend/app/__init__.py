from flask import Flask
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend-backend communication
    app.config.from_object('instance.config.Config')

    with app.app_context():
        # Import and register blueprints
        from .routes import main_bp
        app.register_blueprint(main_bp)

    return app
