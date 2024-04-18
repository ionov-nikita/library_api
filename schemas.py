from marshmallow import validates, post_load
from flasgger import Schema, fields, ValidationError

from models import get_book_by_title, Book, Author


class AuthorSchema(Schema):
    author_id = fields.Int(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)

    @validates("author_id")
    def validate_id(self, author_id: int) -> None:
        if not author_id:
            raise ValidationError("author_id not sent")

    @validates("first_name")
    def validate_id(self, first_name: int) -> None:
        if not first_name:
            raise ValidationError("first_name not sent")

    @validates("last_name")
    def validate_id(self, last_name: int) -> None:
        if not last_name:
            raise ValidationError("last_name not sent")

    @post_load
    def create_author(self, data: dict, **kwargs):
        return Author(**data)


class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Nested(AuthorSchema(), required=True)

    @validates("title")
    def validate_title(self, title: str) -> None:
        if get_book_by_title(title) is not None:
            raise ValidationError(
                'Book with title "{title}" already exists, '
                "please use a different title.".format(title=title)
            )

    @post_load
    def create_book(self, data: dict, **kwargs) -> Book:
        return Book(**data)

