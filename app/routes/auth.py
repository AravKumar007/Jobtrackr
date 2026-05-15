from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db, bcrypt
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags: [Auth]
    parameters:
      - in: body
        name: body
        schema:
          required: [name, email, password]
          properties:
            name: {type: string, example: "Rahul Sharma"}
            email: {type: string, example: "rahul@email.com"}
            password: {type: string, example: "secret123"}
    responses:
      201:
        description: Registered successfully
      409:
        description: Email already exists
    """
    data = request.get_json()

    if not data or not all(k in data for k in ("name", "email", "password")):
        return jsonify({"error": "name, email and password are required"}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=data["email"].lower()).first():
        return jsonify({"error": "Email already registered"}), 409

    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(name=data["name"], email=data["email"].lower(), password_hash=password_hash)

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Registered successfully", "token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login and get JWT token
    ---
    tags: [Auth]
    parameters:
      - in: body
        name: body
        schema:
          required: [email, password]
          properties:
            email: {type: string, example: "rahul@email.com"}
            password: {type: string, example: "secret123"}
    responses:
      200:
        description: Login successful, returns token
      401:
        description: Invalid credentials
    """
    data = request.get_json()

    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=data["email"].lower()).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Login successful", "token": token, "user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Get current logged-in user
    ---
    tags: [Auth]
    security:
      - Bearer: []
    responses:
      200:
        description: Current user details
    """
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200
