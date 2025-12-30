# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import os
import dateutil.parser
import babel
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from jinja2 import filters
from sqlalchemy import or_
import config
from forms import *
from flask_migrate import Migrate
from models import Artist, Genre, Show, Venue, db
from seeds import seed_data
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
moment = Moment(app)
app.config.from_object("config")
# DONE: connect to a local postgresql database
db.init_app(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    if isinstance(value, datetime):
        date = value
    else:
        date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


def get_genres(genres: list[Genre]):
    return [genre.name for genre in genres if genre is not None]


def get_filtered_genres(words):
    filters = [Genre.name.ilike(f"%{word}%") for word in words]
    return Genre.query.filter(or_(*filters)).all()


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    all_venues: list[Venue] = Venue.query.all()
    if not all_venues:
        return render_template("pages/venues.html", areas=[])
    datadictionary = {}
    for venue in all_venues:
        keyvenue = f"{venue.city}-{venue.state}"
        locationvenue = {"city": venue.city, "state": venue.state, "venues": []}
        if keyvenue not in datadictionary:
            datadictionary[keyvenue] = locationvenue
        total_shows = (
            db.session.query(Show)
            .join(Venue)
            .filter((venue.id == Show.venue_id) & (Show.start_time > datetime.now()))
            .all()
        )
        count_upcoming = len(total_shows)
        datadictionary[keyvenue]["venues"].append(
            {"id": venue.id, "name": venue.name, "num_upcoming_shows": count_upcoming}
        )
    data = []
    for value in datadictionary.values():
        data.append(value)
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # DONE implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")
    venues: list[Venue] = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(venues),
        "data": [],
    }
    for venue in venues:
        total_shows = (
            db.session.query(Show)
            .join(Venue)
            .filter((venue.id == Show.venue_id) & (Show.start_time > datetime.now()))
            .all()
        )
        total_shows = len(total_shows)
        response["data"].append(
            {"id": venue.id, "name": venue.name, "num_upcoming_shows": total_shows}
        )

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=search_term,
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    venue: Venue = Venue.query.get_or_404(venue_id)
    past_shows = []
    upcomming_shows = []
    results = (
        db.session.query(Show, Artist)
        .join(Artist, Show.artist_id == Artist.id)
        .filter(Show.venue_id == venue_id)
        .all()
    )
    for show, artist in results:
        temp_show = {
            "artist_id": show.artist_id,
            "start_time": show.start_time,
            "artist_image_link": artist.image_link,
        }
        if show.start_time > datetime.now():
            upcomming_shows.append(temp_show)
        else:
            past_shows.append(temp_show)
    data = {
        **venue.to_dict(),
        "past_shows": past_shows,
        "upcoming_shows": upcomming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcomming_shows),
        "genres": get_genres(venue.genres),
    }
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    form = VenueForm()
    if form.validate_on_submit():
        data = form.data
        data["website"] = data.pop("website_link")
        data.pop("csrf_token")
        genres = db.session.query(Genre).filter(Genre.name.in_(data["genres"])).all()
        data["genres"] = genres
        temp_venue = Venue(**data)
        db.session.add(temp_venue)
        try:
            db.session.commit()
            flash(f"Venue {temp_venue.name} is saved in db")
        except Exception as e:
            db.session.rollback()
            flash("An error ocurred. Vene is not saved in db")
    else:
        flash(
            f"An error ocurred. Venue {request.form['name']} cound not be listed. There's probably a field missing."
        )
    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<int:venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash("Venue fue eliminado exitosamente.")
        return jsonify({"success": True}), 200
    except Exception:
        db.session.rollback()
        flash("Venue no sepudo eliminar")
        return jsonify({"success": False}), 500
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 0,
        "data": [],
    }
    search_term = request.form.get("search_term", "")
    artists: list[Artist] = (
        Artist.query.with_entities(Artist.id, Artist.name)
        .filter(Artist.name.ilike(f"%{search_term}%"))
        .all()
    )
    for artist in artists:
        response["data"].append(
            {"id": artist.id, "name": artist.name, "num_upcoming_shows": 0}
        )
    response["count"] = len(artists)
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>", methods=["GET"])
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # DONE: replace with real artist data from the artist table, using artist_id

    try:
        artist: Artist = Artist.query.get_or_404(artist_id)
        shows = (
            db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).all()
        )
        upcoming_shows = []
        past_shows = []
        results = (
            db.session.query(Show, Venue)
            .join(Venue, Show.venue_id == Venue.id)
            .filter(Show.artist_id == artist_id)
            .all()
        )
        for show, venue in results:
            temp_show = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time,
            }
            if show.start_time > datetime.now():
                upcoming_shows.append(temp_show)
            else:
                past_shows.append(temp_show)
        data = {
            **artist.to_dict(),
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows),
            "genres": [g.name for g in artist.genres],
        }
    except Exception:
        flash("Error, may have been caused by the artist bot being found")
        return render_template("pages/home.html")

    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    # DONE: populate form with fields from artist with ID <artist_id>
    artist: Artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    form.genres.data = get_genres(artist.genres)
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    try:
        if form.validate_on_submit():
            genres = form.genres.data
            del form.genres
            form.populate_obj(artist)
            artist.genres = get_filtered_genres(genres)
            db.session.add(artist)
            db.session.commit()
            flash("Updated artist")
        else:
            flash("Incorrect updated artist", "error")
    except Exception as e:
        db.session.rollback()
        flash("Error in server")
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    # DONE: populate form with values from venue with ID <venue_id>
    try:
        venue: Venue = Venue.query.get_or_404(venue_id)
        form = VenueForm(obj=venue)
        form.genres.data = get_genres(venue.genres)
    except Exception as e:
        flash("Venue does not exist", "danger")
        raise e
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # DONE  take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = Venue.query.get_or_404(venue_id)
        form = VenueForm(obj=venue)
        if form.validate_on_submit():
            genres = form.genres.data
            del form.genres
            form.populate_obj(obj=venue)
            venue.genres = get_filtered_genres(genres)
            db.session.add(venue)
            db.session.commit()
        else:
            flash("Invalid data")
    except Exception as e:
        flash("Error in server")
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    form = ArtistForm()
    if form.validate_on_submit():
        data = form.data
        data.pop("csrf_token")
        data["website"] = data.pop("website_link")
        genres = db.session.query(Genre).filter(Genre.name.in_(data["genres"])).all()
        data["genres"] = genres
        artist = Artist(**data)
        db.session.add(artist)
        try:
            db.session.commit()
            flash(f"Arist {artist.name} was created")
        except Exception as e:
            db.session.rollback()
            flash("Internal error")
    else:
        flash("Invalid data for " + form.data["name"])
    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    shows: list[Show] = Show.query.all()
    data = []
    for show in shows:
        venue: Venue = Venue.query.get(show.venue_id)
        artist: Artist = Artist.query.get(show.artist_id)
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time,
            }
        )
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead
    try:
        form = ShowForm()
        if form.validate_on_submit():
            data = form.data
            del data["csrf_token"]
            show = Show(**data)
            db.session.add(show)
            db.session.commit()
            flash("Show was successfully listed!")
        else:
            flash(f"Error in data", "error")
    except Exception:
        flash("Error in server")
        db.session.rollback()
    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
# if __name__ == "__main__":
#     with app.app_context():
#         db.drop_all()
#         db.create_all()
#         seed_data(db, Venue, Artist, Show)
#     app.run()

# Or specify port manually:
if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data(db, Venue, Artist, Show)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
