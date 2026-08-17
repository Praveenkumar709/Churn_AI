"""
Database migration script to add original_data column to predictions table
Run this script to update your database schema
"""
from sqlalchemy import text, inspect
from database.connection import engine, Base
from db_models.prediction import Prediction

def migrate():
    """Add original_data column to predictions table if it doesn't exist"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('predictions')]
    
    if 'original_data' not in columns:
        print("Adding original_data column to predictions table...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE predictions ADD COLUMN original_data TEXT"))
            conn.commit()
            print("Migration completed successfully!")
    else:
        print("original_data column already exists in predictions table")

if __name__ == "__main__":
    migrate()
