import sqlite3
from dataclasses import dataclass
from typing import Optional, Union, List, Dict

DATA = [
    {"id": 0, "title": "A Byte of Python", "author": "Swaroop C. H."},
    {"id": 1, "title": "Moby-Dick; or, The Whale", "author": "Herman Melville"},
    {"id": 3, "title": "War and Peace", "author": "Leo Tolstoy"},
]

DATABASE_NAME = "table_books.db"
BOOKS_TABLE_NAME = "books"
AUTHOR_TABLE_NAME = "author"


@dataclass
class Author:
    author_id: int
    first_name: str
    last_name: str

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass
class Book:
    title: str
    author: Author
    id: Optional[int] = None

    def __getitem__(self, item: str) -> Union[int, str]:
        return getattr(self, item)


def init_db(initial_records: List[Dict]) -> None:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='{BOOKS_TABLE_NAME}';
            """
        )
        exists = cursor.fetchone()
        if not exists:
            cursor.executescript(
                f"""
                CREATE TABLE `{BOOKS_TABLE_NAME}`(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT,
                    author TEXT
                );
                """
            )
            cursor.executemany(
                f"""
                INSERT INTO `{BOOKS_TABLE_NAME}`
                (title, author) VALUES (?, ?)
                """,
                [(item["title"], item["author"]) for item in initial_records],
            )


def _get_book_obj_from_row(row: tuple) -> Book:
    return Book(id=row[0], title=row[1], author=row[2])


def get_all_books() -> list[Book]:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM `{BOOKS_TABLE_NAME}`")
        all_books = cursor.fetchall()
        return [_get_book_obj_from_row(row) for row in all_books]


def add_book(book: Book) -> Book:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO `{BOOKS_TABLE_NAME}` 
            (title, author) VALUES (?, ?)
            """,
            (book.title, book.author.author_id),
        )
        book.id = cursor.lastrowid
        return book


def add_author(author: Author):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        sql_request = f"""
        INSERT INTO '{AUTHOR_TABLE_NAME}' 
        (first_name, last_name) VALUES (?, ?)
        """
        cursor.execute(sql_request, (author.first_name, author.last_name))


def get_book_by_id(book_id: int) -> Optional[Book]:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT * FROM `{BOOKS_TABLE_NAME}` WHERE id = ?
            """,
            (book_id,),
        )
        book = cursor.fetchone()
        if book:
            return _get_book_obj_from_row(book)


def update_book_by_id(book: Book, book_id) -> None:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            UPDATE {BOOKS_TABLE_NAME}
            SET title = ?, author = ?
            WHERE id = ?
            """,
            (book.title, book.author.author_id, book_id),
        )
        conn.commit()


def delete_book_by_id(book_id: int) -> None:
    book = get_book_by_id(book_id)

    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            DELETE FROM {BOOKS_TABLE_NAME}
            WHERE id = ?
            """,
            (book_id,),
        )
        conn.commit()
    return book


def get_book_by_title(book_title: str) -> Optional[Book]:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT * FROM `{BOOKS_TABLE_NAME}` WHERE title = ?
            """,
            (book_title,),
        )
        book = cursor.fetchone()
        if book:
            return _get_book_obj_from_row(book)


def get_book_by_author(author_id: int):
    with sqlite3.connect(DATABASE_NAME) as con:
        cursor = con.cursor()
        sql_request = f"""
        SELECT b.id, b.title, b.author 
        FROM {AUTHOR_TABLE_NAME} a 
        JOIN {BOOKS_TABLE_NAME} b ON b.id = a.author_id 
        WHERE a.author_id = ?
        """

        cursor.execute(sql_request, (author_id,))
        all_books = cursor.fetchall()
        return [_get_book_obj_from_row(row) for row in all_books]


def new_author(author: Author):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        sql_request = f"""
        INSERT INTO '{AUTHOR_TABLE_NAME}' 
        (author_id, first_name, last_name) VALUES (?, ?, ?)
        """
        cursor.execute(
            sql_request, (author.author_id, author.first_name, author.last_name)
        )


def delete_author_with_books(author_id):
    author = get_author_by_id(author_id)
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        sql_request_1 = f"""
        DELETE FROM {AUTHOR_TABLE_NAME} WHERE author_id = ?
        """
        sql_request_2 = f"""
        DELETE FROM {BOOKS_TABLE_NAME} WHERE id = ?
        """

        cursor.execute(sql_request_1, (author_id,))
        cursor.execute(sql_request_2, (author_id,))
    return author


def get_author_by_id(author_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        sql_request = f"""
        SELECT *
        FROM {AUTHOR_TABLE_NAME} WHERE id = ?
        """

        cursor.execute(sql_request, (author_id,))
        result = cursor.fetchall()
        return Author(author_id=result[0][0], first_name=result[0][1], last_name=result[0][2])
