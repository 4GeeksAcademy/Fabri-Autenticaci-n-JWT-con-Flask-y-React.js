import os
import json
import time
import hmac
import hashlib
import base64

from flask import request, jsonify, Blueprint
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from api.models import db, User

api = Blueprint("api", __name__)
CORS(api)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def create_token(payload: dict, expires_in_seconds: int = 60 * 60) -> str:
    
    secret = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")

    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())

    payload = dict(payload)
    payload["iat"] = now
    payload["exp"] = now + int(expires_in_seconds)

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_token(token: str) -> dict:
   
    secret = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")

    parts = token.split(".")
    if len(parts) != 3:
        raise Exception("Invalid token format")

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    expected_sig_b64 = _b64url_encode(expected_sig)

    if not hmac.compare_digest(expected_sig_b64, sig_b64):
        raise Exception("Invalid token signature")

    payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))

    now = int(time.time())
    if now > int(payload.get("exp", 0)):
        raise Exception("Token expired")

    return payload

def get_bearer_token():
   
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth.replace("Bearer ", "", 1).strip()



@api.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello! I'm a message that came from the backend."}), 200


@api.route("/signup", methods=["POST"])
def signup():
    
    body = request.get_json(silent=True) or {}
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return jsonify({"msg": "email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 400

    user = User(email=email, password=generate_password_hash(password), is_active=True)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created"}), 200


@api.route("/token", methods=["POST"])
def token():
   
    body = request.get_json(silent=True) or {}
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return jsonify({"msg": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Bad email or password"}), 401

    token = create_token({"sub": user.id})
    return jsonify({"token": token}), 200


@api.route("/private", methods=["GET"])
def private():
   
    token = get_bearer_token()
    if not token:
        return jsonify({"msg": "Missing Bearer token"}), 401

    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        user = User.query.get(user_id)

        if not user:
            return jsonify({"msg": "User not found"}), 404

        return jsonify({"msg": "Private content", "user": user.serialize()}), 200
    except Exception:
        return jsonify({"msg": "Invalid or expired token"}), 401