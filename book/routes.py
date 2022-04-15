from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from models import Book, db

book_blueprint = Blueprint('book_api_routes', __name__, url_prefix='/api/book')

#Gets all the book details saved in the database.
@book_blueprint.route('/all', methods=['GET'])
def get_all_books():
    all_books = Book.query.all()
    result = [book.serialize() for book in all_books]
    response = {"result":result}
    return jsonify(response)

#Save the details of the book into the database.
@book_blueprint.route('/create', methods=['POST'])
def create_books():
    try:
        book = Book()
        book.name = request.form['name']
        book.slug = request.form['slug']
        book.author_name = request.form['author_name']
        book.published_year = request.form['published_year']
        db.session.add(book)
        db.session.commit()

        response = {'message': 'Book Create', 'result': book.serialize()}
    except Exception as e:
        print(str(e))
        response = {'message': 'Book creation failed'}

    return jsonify(response)

#Retrives details of the book based on the slug id.
@book_blueprint.route('/<slug>', methods=['GET'])
def book_details(slug):
    book = Book.query.filter_by(slug=slug).first()
    if book:
        response = {"result":book.serialize()}
    else:
        response = {"message":"No books found"}

    return jsonify(response)

#Returns True if book already exists in the database, otherwise returns false. 
@book_blueprint.route('/exists/<bookname>/<slugname>', methods=['GET'])
def book_exists(bookname,slugname):
    book = Book.query.filter(or_(Book.name==bookname , Book.slug==slugname)).first()
    if book:
        return jsonify({"result": True}), 200
    return jsonify({"result": False}), 404

    
