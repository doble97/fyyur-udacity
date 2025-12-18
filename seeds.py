from datetime import datetime


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
        id=1,
        name="The Musical Hop",
        city="San Francisco",
        state="CA",
        address="1015 Folsom St",
        phone="123-123-1234",
        facebook_link="https://www.facebook.com/TheMusicalHop",
    )
    v2 = Venue(
        id=3,
        name="Park Square Live Music & Coffee",
        city="San Francisco",
        state="CA",
        address="34 Whiskey Moore Ave",
        phone="415-000-1234",
        facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    )
    v3 = Venue(
        id=2,
        name="The Dueling Pianos Bar",
        city="New York",
        state="NY",
        address="335 Delancey Street",
        phone="914-003-1132",
        facebook_link="https://www.facebook.com/theduelingpianos",
    )
    # --- Crear Artistas ---
    a1 = Artist(
        id=4,
        name="Guns N Petals",
        city="San Francisco",
        state="CA",
        phone="326-123-5000",
        genres="Rock n Roll",
    )

    # --- Crear Shows ---
    # Show pasado
    s1 = Show(venue_id=1, artist_id=4, start_time=datetime(2019, 5, 21, 21, 30, 0))
    # Show futuro
    s2 = Show(venue_id=3, artist_id=4, start_time=datetime(2028, 12, 1, 20, 0, 0))

    db.session.add_all([v1, v2, v3, a1, s1, s2])

    try:
        db.session.commit()
        print("¡Base de datos poblada con éxito!")
    except Exception as e:
        db.session.rollback()
        print(f"Error en el seed: {e}")
