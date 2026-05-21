from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth_bp", __name__)


# -------------------------
# REGISTER
# -------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication

    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: admin

            password:
              type: string
              example: admin123

            role:
              type: string
              enum:
                - admin
                - user
              example: admin

    responses:
      201:
        description: User registered successfully

      400:
        description: Validation error
    """

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body required"
        }), 400

    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    if not username or not password:
        return jsonify({
            "success": False,
            "message":
            "Username and password are required"
        }), 400

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "User already exists"
        }), 400

    new_user = User(
        username=username,
        role=role
    )

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message":
        "User created successfully"
    }), 201


# -------------------------
# LOGIN
# -------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user and get JWT token
    ---
    tags:
      - Authentication

    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: admin

            password:
              type: string
              example: admin123

    responses:
      200:
        description: Login successful

      401:
        description: Invalid credentials
    """

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message":
            "Request body required"
        }), 400

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(
        username=username
    ).first()

    if (
        not user
        or not user.check_password(password)
    ):
        return jsonify({
            "success": False,
            "message":
            "Invalid credentials"
        }), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    return jsonify({
        "success": True,
        "access_token": access_token,
        "role": user.role
    }), 200