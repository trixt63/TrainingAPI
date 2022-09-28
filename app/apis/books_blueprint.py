import uuid

import jwt
from sanic import Blueprint
from sanic.response import json

from app.constants.cache_constants import CacheConstants
from app.databases.mongodb import MongoDB
from app.databases.redis_cached import get_cache, set_cache
from app.decorators.auth import protected
from app.decorators.json_validator import validate_with_jsonschema
from app.hooks.error import ApiInternalError, ApiForbidden, ApiNotFound, ApiUnauthorized
from app.models.book import Book, create_book_json_schema, update_book_json_schema
from app.utils.logger_utils import get_logger
from config import Config

books_bp = Blueprint('books_blueprint', url_prefix='/books')

_db = MongoDB()

logger = get_logger("Books blueprint")

@books_bp.get('/')
async def get_all_books(request):
    # TODO: use cache to optimize api
    async with request.app.ctx.redis as r:
        books = await get_cache(r, CacheConstants.all_books)
        if books is None:
            try:
                book_objs = _db.get_books()
                books = [book.to_dict() for book in book_objs]
                await set_cache(r, CacheConstants.all_books, books)
            except Exception as ex:
                logger.exception(ex)

    number_of_books = len(books)
    return json({
        'n_books': number_of_books,
        'books': books
    })


@books_bp.route('/', methods={'POST'})
@validate_with_jsonschema(create_book_json_schema)  # To validate request body
@protected  # TODO: Authenticate
async def create_book(request, username=None):
    body = request.json

    book_id = str(uuid.uuid4())
    book = Book(book_id).from_dict(body)
    book.owner = username

    # Save book to database
    inserted = _db.add_book(book)
    if not inserted:
        raise ApiInternalError('Fail to create book')

    # TODO: Update cache

    return json({
        'status': 'success',
    })


# api get, update, delete book

@books_bp.route('/<book_id>', methods={'GET'})
async def get_book(request, book_id):
    book_obj = _db.get_book_by_id(book_id=book_id)
    if not book_obj:
        raise ApiNotFound('Not found book')
    book = book_obj.to_dict()
    return json(book)


@books_bp.route('/<book_id>', methods={'PUT'})
@validate_with_jsonschema(update_book_json_schema)  # To validate request body
@protected
async def update_book(request, book_id, username=None):
    body = request.json
    book_obj = Book(book_id).from_dict(body)
    book_obj.owner = username
    # check owner
    to_be_updated = _db.get_book_by_id(book_id)  # get to-be-updated book
    if not to_be_updated:
        raise ApiNotFound('Not found book')
    if to_be_updated.owner != username:
        raise ApiForbidden('You are not the owner')  # raise 403 Forbidden
    else:
        # check if fields are null, then fill the null fields
        book_dict = book_obj.to_dict()
        to_be_updated_dict = to_be_updated.to_dict()
        for attr, val in book_dict.items():
            if val is None or val == "":
                book_dict[attr] = to_be_updated_dict[attr]
        book_obj = Book(book_id).from_dict(book_dict)
        updated = _db.update_book(filter_={'_id':book_id}, book=book_obj)

    if not updated:
        raise ApiInternalError('Fail to update book')

    return json({
        'status': "success",
    })


@books_bp.route('/<book_id>', methods={'DELETE'})
@protected
async def delete_book(request, book_id, username=None):
    to_be_deleted = _db.get_book_by_id(book_id)  # get to-be-deleted book
    if not to_be_deleted:
        raise ApiNotFound('Not found book')
    if to_be_deleted.owner != username:
        raise ApiForbidden('You are not the owner')  # raise 403 Forbidden
    deleted = _db.delete_book(filter_={'_id': book_id})
    if not deleted.deleted_count:
        raise ApiInternalError('Fail to delete book')
    return json({
        'status': "success"
    })