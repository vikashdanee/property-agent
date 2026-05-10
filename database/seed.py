# database/seed.py
from database.connection import engine, get_db_session
from database.models import Base, Unit, Resident

def create_tables():
    """Create all tables."""
    Base.metadata.create_all(engine)
    print("Tables created.")

def seed_data():
    """Seed initial data."""
    db = get_db_session()
    try:
        # Only seed if empty
        if db.query(Unit).count() > 0:
            print("Data already exists — skipping seed.")
            return

        # Units
        units = [
            Unit(beds=2, rent=1400, location="downtown", available=True,
                 address="12 Main St",    amenities="parking, gym"),
            Unit(beds=1, rent=950,  location="midtown",  available=True,
                 address="45 Park Ave",   amenities="laundry"),
            Unit(beds=3, rent=2100, location="downtown", available=False,
                 address="8 River Rd",    amenities="parking, pool, gym"),
            Unit(beds=2, rent=1350, location="uptown",   available=True,
                 address="22 Hill St",    amenities="laundry, parking"),
            Unit(beds=1, rent=870,  location="downtown", available=True,
                 address="5 Oak Lane",    amenities="laundry"),
        ]
        db.add_all(units)

        # Residents
        residents = [
            Resident(unit_id=1, name="Vikash", email="vikash@email.com",  phone="971-555-0101"),
            Resident(unit_id=2, name="Sarah",  email="sarah@email.com",   phone="971-555-0102"),
            Resident(unit_id=4, name="James",  email="james@email.com",   phone="971-555-0104"),
            Resident(unit_id=5, name="Priya",  email="priya@email.com",   phone="971-555-0105"),
        ]
        db.add_all(residents)

        db.commit()
        print(f"Seeded {len(units)} units and {len(residents)} residents.")

    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    seed_data()