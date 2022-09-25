from main import app
import json
import unittest


class UsersTests(unittest.TestCase):
    """ Unit testcases for REST APIs """

    def test_register(self):
        # with open('./test_info.json', 'r') as f:
        #     register_info = json.loads(f.read()).get("user")
        register_info = {
            'username': 'MarkZuckerberg',
            'password': '12345678'
        }
        request, response = app.test_client.post('/users/register', data=json.dumps(register_info))
        self.assertEqual(200, response.status)

if __name__ == '__main__':
    unittest.main()