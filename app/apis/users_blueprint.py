import uuid
import bcrypt
import jwt

from sanic import Blueprint, text
from sanic.response import json

from app.databases.mongodb import MongoDB
from app.decorators.auth import protected
from app.decorators.json_validator import validate_with_jsonschema
from app.hooks.error import ApiInternalError
from app.models.user import register_json_schema, User
from app.utils.jwt_utils import generate_jwt

users_bp = Blueprint('users_blueprint', url_prefix='/users')

_db = MongoDB()


@users_bp.route('/register', methods={'POST'})
@validate_with_jsonschema(register_json_schema)  # To validate request body
async def register(request):
    body = request.json
    username = body.get('username')
    b_password = bytes(body.get('password'), 'utf-8')
    password = bcrypt.hashpw(b_password, bcrypt.gensalt())  # hash password
    user = User(username=username, password=password)
    registered = _db.register(user=user)
    if not registered:
        raise ApiInternalError('Fail to register')

    return json({
        'status': "success",
    })


@users_bp.route('/login', methods={'POST'})
async def log_in(request):
    body = request.json
    username = body.get('username')
    b_password = bytes(body.get('password'), 'utf-8')
    user_info = _db.get_user(username)
    hashed_password = user_info.get('password')
    if bcrypt.checkpw(b_password, hashed_password):
        # generate JWT
        token = generate_jwt(username)
        return text(token)
    else:
        return json({'status': "Login failed"})