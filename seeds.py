from datetime import datetime

from models import Artist


data1 = {
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [
        {
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
            "start_time": "2019-05-21T21:30:00.000Z",
        }
    ],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
}
data2 = {
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2019-06-15T23:00:00.000Z",
        }
    ],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
}
data3 = {
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-01T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-08T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-15T20:00:00.000Z",
        },
    ],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
}
artist_list = [data1, data2, data3]


def getArtist(position: int):
    data = artist_list[position]
    new_artist = Artist(
        id=data["id"],
        name=data["name"],
        genres=",".join(data["genres"]),
        city=data["city"],
        state=data["state"],
        phone=data["phone"],
        facebook_link=data.get("facebook_link"),
        image_link=data.get("image_link"),
        website=data.get("website"),
        seeking_venue=data.get("seeking_venue", False),
        seeking_description=data.get("seeking_description"),
    )
    return new_artist


def seed_data(db, Venue, Artist, Show):
    """
    Puebla la base de datos con datos iniciales.
    Recibe db y los modelos como argumentos para evitar importaciones circulares.
    """
    print("Iniciando limpieza de tablas...")
    Show.query.delete()
    Artist.query.delete()
    Venue.query.delete()

    # --- Crear Venues ---
    v1 = Venue(
        name="The Musical Hop",
        city="San Francisco",
        state="CA",
        address="1015 Folsom St",
        phone="123-123-1234",
        facebook_link="https://www.facebook.com/TheMusicalHop",
    )
    v2 = Venue(
        name="Park Square Live Music & Coffee",
        city="San Francisco",
        state="CA",
        address="34 Whiskey Moore Ave",
        phone="415-000-1234",
        facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    )
    v3 = Venue(
        name="The Dueling Pianos Bar",
        city="New York",
        state="NY",
        address="335 Delancey Street",
        phone="914-003-1132",
        facebook_link="https://www.facebook.com/theduelingpianos",
    )
    db.session.add_all([v1, v2, v3])
    db.session.flush()

    # Create artists
    a1 = getArtist(0)
    a2 = getArtist(1)
    a3 = getArtist(2)
    db.session.add_all([a1, a2, a3])
    db.session.flush()
    # --- Crear Shows ---
    # Show pasado
    s1 = Show(
        venue_id=v1.id, artist_id=a1.id, start_time=datetime(2019, 5, 21, 21, 30, 0)
    )
    # Show futuro
    s2 = Show(
        venue_id=v1.id, artist_id=a1.id, start_time=datetime(2028, 12, 1, 20, 0, 0)
    )

    db.session.add_all([s1, s2])

    try:
        db.session.commit()
        print("¡Base de datos poblada con éxito!")
    except Exception as e:
        db.session.rollback()
        print(f"Error en el seed: {e}")
