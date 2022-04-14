from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.app = app
    db.init_app(app)

#The book model having information about book like author name, slug, published year etc. 
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    author_name = db.Column(db.String(150), nullable=False)
    published_year = db.Column(db.String(255))

    def __repr__(self):
        return f'<book {self.id} {self.name}>'

    #method to serialize the book model. 
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'author_name': self.author_name,
            'published_year': self.published_year,
        }
