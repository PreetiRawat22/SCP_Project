import requests

from . import BOOK_API_URL


class BookClient:
    @staticmethod
    def get_books():
        response = requests.get(BOOK_API_URL + '/api/book/all')
        return response.json()

    @staticmethod
    def get_book(slug):
        response = requests.get(BOOK_API_URL + '/api/book/' + slug)
        return response.json()

    @staticmethod
    def add_book(form):
        book = None
        payload = {
            'name': form.name.data,
            'slug': form.slug.data,
            'author_name': form.author_name.data,
            'published_year' : form.published_year.data
        }
        url = BOOK_API_URL + '/api/book/create'
        response = requests.request("POST", url=url, data=payload)
        if response:
            book = response.json()
            print(book)
        return book
    