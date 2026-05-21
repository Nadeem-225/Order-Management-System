from flask import Flask
from flasgger import Swagger
from extensions import db, jwt
from routes.order_routes import order_bp
from routes.auth_routes import auth_bp
from datetime import timedelta
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
import os

load_dotenv()

app = Flask(__name__)

# -------------------------
# DATABASE CONFIG
# -------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# -------------------------
# JWT CONFIG
# -------------------------
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)


# -------------------------
# SWAGGER JWT AUTH CONFIG
# -------------------------
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Order Management API",
        "description": "API for managing orders with JWT authentication and priority scheduling",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": (
                "Enter JWT token like:\n"
                "Bearer your_token_here"
            )
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}


# -------------------------
# INIT EXTENSIONS
# -------------------------
db.init_app(app)
jwt.init_app(app)

Swagger(
    app,
    config=swagger_config,
    template=swagger_template
)


# -------------------------
# REGISTER BLUEPRINTS
# -------------------------
app.register_blueprint(
    order_bp,
    url_prefix="/api/v1"
)

app.register_blueprint(
    auth_bp,
    url_prefix="/api/v1"
)


# -------------------------
# HOME ROUTE
# -------------------------
@app.route("/")
def home():
    return {
        "success": True,
        "message": "Order Management System API Running"
    }


# -------------------------
# GLOBAL ERROR HANDLER
# -------------------------
@app.errorhandler(Exception)
def handle_exception(error):

    if isinstance(error, HTTPException):
        return {
            "success": False,
            "message": error.name,
            "error": error.description
        }, error.code

    return {
        "success": False,
        "message": "Internal Server Error",
        "error": str(error)
    }, 500


# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )