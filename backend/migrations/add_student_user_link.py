"""Add user_id column to students table and link existing students to users"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        # Add user_id column if it doesn't exist
        try:
            conn.execute(text('ALTER TABLE students ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE'))
            print('Added user_id column to students table')
        except Exception as e:
            if 'already exists' in str(e).lower() or 'duplicate column' in str(e).lower():
                print('user_id column already exists')
            else:
                print(f'Note: {e}')
        
        # Create index
        try:
            conn.execute(text('CREATE INDEX ix_students_user_id ON students(user_id)'))
            print('Created index ix_students_user_id')
        except Exception as e:
            if 'already exists' in str(e).lower():
                print('Index already exists')
            else:
                print(f'Note: {e}')
        
        # Link existing students to users by matching names
        result = conn.execute(text('''
            UPDATE students s
            SET user_id = u.id
            FROM users u
            WHERE s.user_id IS NULL 
            AND LOWER(s.name) = LOWER(u.full_name)
        '''))
        print(f'Linked {result.rowcount} existing students to users by name')
        
        conn.commit()
        print('Migration complete!')

if __name__ == '__main__':
    migrate()
