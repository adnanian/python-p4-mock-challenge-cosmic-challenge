from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates='planet', cascade='all, delete-orphan')
    scientists = association_proxy('missions', 'scientist', creator=lambda scientist_obj: Mission(scientist=scientist_obj))

    # Add serialization rules
    
    serialize_rules = (
        '-missions.planet',
        '-scientists.planet'
    )


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)

    # Add relationship
    missions = db.relationship('Mission', back_populates='scientist', cascade='all, delete-orphan')
    planets = association_proxy('missions', 'planet', creator=lambda planet_obj: Mission(planet=planet_obj))

    # Add serialization rules
    serialize_rules = (
        '-missions.scientist',
        '-planets.scientist'
    )

    # Add validation
    @validates('name', 'field_of_study')
    def validate_field(self, key, attribute):
        if not attribute:
            raise ValueError(f"{key.title()} cannot be null.")
        return attribute


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # Add relationships
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    
    planet = db.relationship('Planet', back_populates='missions')
    scientist = db.relationship('Scientist', back_populates='missions')

    # Add serialization rules
    serialize_rules = (
        '-planet.missions',
        '-scientist.missions'
    )

    # Add validation
    @validates('name')
    def validate_name(self, key, name):
        if not(name and isinstance(name, str)):
            raise ValueError("Name must be a non-empty string.")
        return name
    
    @validates('planet_id', 'scientist_id')
    def validate_id(self, key, id):
        if type(id) is not int:
            raise ValueError(f"{key.title()} must be an int.")
        return id

# add any models you may need.
