"""Add mentor_id field to courses table to link mentors to their courses"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        # Add mentor_id column with foreign key to users table
        try:
            conn.execute(text('ALTER TABLE courses ADD COLUMN mentor_id INTEGER'))
            print('Added mentor_id column')
        except Exception as e:
            if 'already exists' in str(e).lower() or 'duplicate column' in str(e).lower():
                print('mentor_id column already exists')
            else:
                print(f'Note: {e}')
        
        # Add index on mentor_id for faster queries
        try:
            conn.execute(text('CREATE INDEX IF NOT EXISTS ix_courses_mentor_id ON courses(mentor_id)'))
            print('Added index on mentor_id')
        except Exception as e:
            if 'already exists' in str(e).lower():
                print('Index already exists')
            else:
                print(f'Note creating index: {e}')
        
        conn.commit()
        print('Migration completed: mentor_id added to courses table')

def rollback():
    with engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE courses DROP COLUMN mentor_id'))
            print('Removed mentor_id column')
        except Exception as e:
            print(f'Rollback error: {e}')
        conn.commit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
