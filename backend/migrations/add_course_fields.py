"""Add new fields to courses table (duration_hours, instructor, rating, thumbnail_url)"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        # Add duration_hours column
        try:
            conn.execute(text('ALTER TABLE courses ADD COLUMN duration_hours FLOAT DEFAULT 0.0'))
            print('Added duration_hours column')
        except Exception as e:
            if 'already exists' in str(e).lower():
                print('duration_hours column already exists')
            else:
                print(f'Note: {e}')
        
        # Add instructor column
        try:
            conn.execute(text("ALTER TABLE courses ADD COLUMN instructor VARCHAR(255) DEFAULT 'ElevateED Instructor'"))
            print('Added instructor column')
        except Exception as e:
            if 'already exists' in str(e).lower():
                print('instructor column already exists')
            else:
                print(f'Note: {e}')
        
        # Add rating column
        try:
            conn.execute(text('ALTER TABLE courses ADD COLUMN rating FLOAT DEFAULT 0.0'))
            print('Added rating column')
        except Exception as e:
            if 'already exists' in str(e).lower():
                print('rating column already exists')
            else:
                print(f'Note: {e}')
        
        # Add thumbnail_url column
        try:
            conn.execute(text('ALTER TABLE courses ADD COLUMN thumbnail_url VARCHAR(512)'))
            print('Added thumbnail_url column')
        except Exception as e:
            if 'already exists' in str(e).lower():
                print('thumbnail_url column already exists')
            else:
                print(f'Note: {e}')
        
        conn.commit()
        print('Migration complete!')

if __name__ == '__main__':
    migrate()
