from main import app
import json
import unittest
import jwt

from config import Config


class BooksTests(unittest.TestCase):
    """ Unit testcases for REST APIs """
    def test_get_all_books(self):
        request, response = app.test_client.get('/books')
        self.assertEqual(response.status, 200)
        data = json.loads(response.text)
        books = data.get('books')
        n_books = data.get('n_books')
        self.assertGreaterEqual(n_books, 0)
        self.assertIsInstance(books, list)

    # TODO: unittest for another apis
    def test_get_book(self):
        # get all books
        request, response = app.test_client.get('/books')
        data = json.loads(response.text)
        books = data.get('books')
        book_id = books[-1].get('_id')  # get _id of the last book
        print(f"Book: {books[-1]}")
        # get book by id
        requests, response = app.test_client.get(f'/books/{book_id}')
        self.assertEqual(response.status, 200)
        data = json.loads(response.text)
        self.assertIsInstance(data, dict)

    def test_create_book(self):
        # login
        user_info = {
            "username": "MarkZuckerberg",
            "password": "12345678",
        }
        request, response = app.test_client.post('/users/login', data=json.dumps(user_info))
        data = json.loads(response.text)
        jw_token = data.get('jwt')
        # test create book
        book_info = {
            "title": "Frankenstein",
            "authors": ["Shelley, Mary"],
            "publisher": "Gutenberg project",
            "description": "A scientist created a conscious monster"
        }
        request, response = app.test_client.post(
            '/books', data=json.dumps(book_info), headers={'Authorization': jw_token})
        self.assertEqual(response.status, 200)

    def test_update_book(self):
        # get id of a book
        request, response = app.test_client.get('/books')
        data = json.loads(response.text)
        books = data.get('books')
        book_id = books[-1].get('_id')  # get _id of the last book
        username = books[-1].get('owner')
        # login
        login_info = {
            "username": username,
            "password": "12345678",
        }
        request, response = app.test_client.post('/users/login', data=json.dumps(login_info))
        data = json.loads(response.text)
        jw_token = data.get('jwt')
        # test update book
        update_info = {
            'title': books[-1].get('title') + " (updated)",
            'authors': books[-1].get('authors'),
            'publisher': books[-1].get('publisher'),
            'description': books[-1].get('description')
        }
        print(update_info)
        request, response = app.test_client.put(
            f'/books/{book_id}', data=json.dumps(update_info), headers={"Authorization": jw_token})
        self.assertEqual(response.status, 200)

    # def test_delete_book(self):
    #     # login
    #     login_info = {
    #         "username": "MarkZuckerberg",
    #         "password": "12345678",
    #     }
    #     request, response = app.test_client.post('/users/login', data=json.dumps(login_info))
    #     data = json.loads(response.text)
    #     jw_token = data.get('jwt')
    #     # get id of a book
    #     request, response = app.test_client.get('/books')
    #     data = json.loads(response.text)
    #     books = data.get('books')
    #     book_id = books[-1].get('_id')  # get _id of the last book
    #     # test delete book
    #     request, response = app.test_client.delete(
    #         f'/books/{book_id}', headers={"Authorization": jw_token})
    #     self.assertEqual(response.status, 200)


if __name__ == '__main__':
    unittest.main()
