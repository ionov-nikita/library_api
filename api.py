from flask import Flask, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from flasgger import Swagger, APISpec, swag_from
from apispec_webframeworks.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
import os
from models import (
    DATA,
    get_all_books,
    init_db,
    add_book,
    add_author,
    get_book_by_id,
    delete_book_by_id,
    update_book_by_id,
    get_book_by_author,
    new_author,
    delete_author_with_books,
)
from schemas import BookSchema, AuthorSchema

app = Flask(__name__)
api = Api(app)
spec = APISpec(title='Book',
               version='1.0.0',
               openapi_version='2.0',
               plugins=[FlaskPlugin(), MarshmallowPlugin()]
               )

swagger_path = os.path.abspath('swagger')


class BookList(Resource):
    @swag_from(os.path.join(swagger_path, 'swagger_booklist_get.yml'))
    def get(self) -> tuple[list[dict], int]:
        schema = BookSchema()
        return schema.dump(get_all_books(), many=True), 200

    @swag_from(os.path.join(swagger_path, 'swagger_booklist_post.yml'))
    def post(self) -> tuple[dict, int]:
        data = request.json
        book_schema = BookSchema()
        author_schema = AuthorSchema()
        try:
            book = book_schema.load(data)
            author = author_schema.load(data["author"])

        except ValidationError as exc:
            return exc.messages, 400

        add_author(author)
        book = add_book(book)
        return book_schema.dump(book), 201


class Book(Resource):
    @swag_from(os.path.join(swagger_path, 'swagger_books_get.yml'))
    def get(self, book_id):
        schema = BookSchema()
        book = get_book_by_id(book_id)
        return schema.dump(book)

    @swag_from(os.path.join(swagger_path, 'swagger_books_delete.yml'))
    def delete(self, book_id):
        schema = BookSchema()
        book = delete_book_by_id(book_id)
        return schema.dump(book)

    @swag_from(os.path.join(swagger_path, 'swagger_books_patch.yml'))
    def patch(self, book_id):
        data = request.json
        book_schema = BookSchema()
        try:
            book = book_schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400

        update_book_by_id(book, book_id)
        return book_schema.dump(book)


class Author(Resource):
    def get(self, author_id):
        schema = BookSchema()
        books = get_book_by_author(author_id)
        return schema.dump(books, many=True)

    def post(self):
        data = request.json
        author_schema = AuthorSchema()
        try:
            author = author_schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400

        new_author(author)
        return author_schema.dump(author)

    def delete(self, author_id):
        schema = AuthorSchema()
        author = delete_author_with_books(author_id)
        return schema.dump(author)


swagger = Swagger(app, template_file=os.path.join(swagger_path, 'swagger_authors.json'))

api.add_resource(BookList, "/api/books")
api.add_resource(Book, "/api/books/<int:book_id>")
api.add_resource(Author, "/api/authors/", "/api/authors/<int:author_id>")

if __name__ == "__main__":
    init_db(initial_records=DATA)
    app.run(debug=True, threaded=True)
