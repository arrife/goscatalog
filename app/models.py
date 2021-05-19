from app import db
from sqlalchemy.sql.expression import Executable
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import literal


class FullTextIndex(Executable, db.Column):
    _execution_options = \
        Executable._execution_options.union({'autocommit': True})

    def __init__(self, columns, value):
        self.columns = columns
        self.value = literal(value)


@compiles(FullTextIndex)
def _match(element, compiler, **kw):
    return "MATCH (%s) AGAINST (%s)" % (
               ", ".join(compiler.process(c, **kw) for c in element.columns),
               compiler.process(element.value)
             )


authors = db.Table('authors',
    db.Column('exhibit_inner_id', db.Integer, db.ForeignKey('exhibit.inner_id'), nullable=False),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), nullable=False)
)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    patronymic = db.Column(db.String(30), nullable=False)
    name_init = db.Column(db.String(1), nullable=False)
    patronymic_init = db.Column(db.String(1), nullable=False)

    concat = " "+surname+" "+name+" "+patronymic+" "+surname+" "+name_init+" "+patronymic_init+" "
    fulltext=[surname,name,patronymic,name_init,patronymic_init]

    def __repr__(self):
        return "{} {} {} {} {}".format(self.surname, self.name, self.patronymic, self.name_init, self.patronymic_init)

technologies = db.Table('technologies',
    db.Column('exhibit_inner_id', db.Integer, db.ForeignKey('exhibit.inner_id'), nullable=False),
    db.Column('technology_id', db.Integer, db.ForeignKey('technology.id'), nullable=False)
)

class Technology(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return self.name

class Typology(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    exhibits = db.relationship('Exhibit', backref='typology', lazy=True)

    def __repr__(self):
        return self.name


class Museum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    exhibits = db.relationship('Exhibit', backref='museum', lazy=True)

    def __repr__(self):
        return "id: {}, name: {}".format(self.id, self.name)


class Exhibit(db.Model):
    inner_id = db.Column(db.Integer, primary_key=True)
    museum_id = db.Column(db.Integer, db.ForeignKey('museum.id'), nullable=False)
    typology_id = db.Column(db.Integer, db.ForeignKey('typology.id'))
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    provenance = db.Column(db.Text)
    keywords = db.Column(db.Text)
    comment = db.Column(db.Text)
    typology_desc = db.Column(db.Text)
    period_string = db.Column(db.Text)
    production_place = db.Column(db.Text)
    find_place = db.Column(db.Text)
    start_date = db.Column(db.String(30))
    finish_date = db.Column(db.String(30))
    image = db.Column(db.Text)
    # epoch = db.Column(db.Text)
    authors = db.relationship('Author', secondary=authors, lazy='subquery',
        backref=db.backref('exhibits', lazy=True))
    technologies = db.relationship('Technology', secondary=technologies, lazy='subquery',
        backref=db.backref('exhibits', lazy=True))

    fulltext = [name, description, provenance, keywords,
    comment, typology_desc, period_string, production_place, find_place,
    # epoch,
    ]

    def __repr__(self):
        return "id: {}, name: {}".format(self.inner_id, self.name)
