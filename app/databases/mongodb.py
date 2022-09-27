from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from app.constants.mongodb_constants import MongoCollections
from app.models.book import Book
from app.models.user import User
from app.utils.logger_utils import get_logger
from config import MongoDBConfig

logger = get_logger('MongoDB')


class MongoDB:
    def __init__(self, connection_url=None):
        if connection_url is None:
            connection_url = \
                f'mongodb://{MongoDBConfig.USERNAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}'

        self.connection_url = connection_url.split('@')[-1]
        self.client = MongoClient(connection_url)
        self.db = self.client[MongoDBConfig.DATABASE]

        self._users_col = self.db[MongoCollections.users]
        self._books_col = self.db[MongoCollections.books]

    def get_books(self, filter_=None, projection=None):
        try:
            if not filter_:
                filter_ = {}
            cursor = self._books_col.find(filter_, projection=projection)
            data = []
            for doc in cursor:
                data.append(Book().from_dict(doc))
            return data
        except Exception as ex:
            logger.exception(ex)
        return []

    def add_book(self, book: Book):
        try:
            inserted_doc = self._books_col.insert_one(book.to_dict())
            return inserted_doc
        except Exception as ex:
            logger.exception(ex)
        return None

    # TODO: write functions CRUD with books
    def get_book_by_id(self, book_id):
        try:
            gotten_book = self._books_col.find_one({'_id': book_id})
            return Book().from_dict(gotten_book)
        except Exception as ex:
            logger.exception(ex)
        return None

    def update_book(self, book: Book, filter_=None):
        try:
            updated_doc = self._books_col.update_one(filter_, {"$set": book.to_dict()})
            return updated_doc
        except Exception as ex:
            logger.exception(ex)
        return None

    def delete_book(self, filter_=None):
        try:
            deleted_doc = self._books_col.delete_one(filter_)
            return deleted_doc
        except Exception as ex:
            logger.exception(ex)
        return None

    # TODO: write register/login
    def register(self, user: User):
        try:
            inserted_doc = self._users_col.insert_one(user.to_dict())
            return inserted_doc
        except DuplicateKeyError:
            return "duplicated"
        except Exception as ex:
            logger.exception(ex)

        return None

    def get_user(self, _id=''):
        try:
            user_info = self._users_col.find_one({'_id': _id})
            return user_info
        except Exception as ex:
            print(f"Exception: {ex}")
            logger.exception(ex)
        return None