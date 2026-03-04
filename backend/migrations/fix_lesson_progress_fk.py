"""Fix lesson_progress foreign key to reference users instead of students"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        # Delete orphan records first
        result = conn.execute(text('DELETE FROM lesson_progress WHERE student_id NOT IN (SELECT id FROM users)'))
        print(f'Deleted {result.rowcount} orphan lesson_progress records')
        
        # Drop old constraint
        try:
            conn.execute(text('ALTER TABLE lesson_progress DROP CONSTRAINT IF EXISTS lesson_progress_student_id_fkey'))
            print('Dropped old FK constraint')
        except Exception as e:
            print(f'Note: {e}')
        
        # Add new constraint
        try:
            conn.execute(text('ALTER TABLE lesson_progress ADD CONSTRAINT lesson_progress_student_id_fkey FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE'))
            print('Added new FK constraint referencing users')
        except Exception as e:
            print(f'Note: {e}')
        
        conn.commit()
        print('Migration complete!')

if __name__ == '__main__':
    migrate()
