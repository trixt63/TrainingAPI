import time
import bcrypt


class User:
    def __init__(self, username, password):
        self._id = username
        self._username = username
        self._password = password

    def to_dict(self):
        return {
            '_id': self._id,
            'username': self._username,
            'password': self._password
        }


user_json_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
    },
    'required': ['username', 'password']
}