import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

artist_genre = db.Table(
    "artist_genre",
    db.Column("artist_id", db.Integer, db.ForeignKey("Artist.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("Genre.id"), primary_key=True),
)

venue_genre = db.Table(
    "venue_genre",
    db.Column("venue_id", db.Integer, db.ForeignKey("Venue.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("Genre.id"), primary_key=True),
)


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(300))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(300))
    # genres = db.Column(db.String(120))
    shows = db.relationship(
        "Show", backref="venue", lazy=False, cascade="all, delete-orphan"
    )
    genres = db.relationship("Genre", secondary=venue_genre)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
        }


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    phone = db.Column(db.String(120))
    website = db.Column(db.String(300))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(300))
    shows = db.relationship("Show", backref="artist")
    genres = db.relationship("Genre", secondary=artist_genre)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "seeking_description": self.seeking_description,
            "seeking_venue": self.seeking_venue,
            "image_link": self.image_link,
            "weebsite": self.website,
            "facebook_link": self.facebook_link,
        }


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )


class Genre(db.Model):
    __tablename__ = "Genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
