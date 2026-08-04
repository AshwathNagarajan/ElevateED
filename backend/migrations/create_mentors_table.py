"""Create mentors table for storing mentor-specific information"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        # Create mentors table
        try:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS mentors (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(20),
                    qualification VARCHAR(255) NOT NULL,
                    specialization VARCHAR(255) NOT NULL,
                    experience_years INTEGER NOT NULL DEFAULT 0,
                    bio TEXT,
                    profile_image_url VARCHAR(512),
                    linkedin_url VARCHAR(512),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            '''))
            print('Created mentors table')
        except Exception as e:
            if 'already exists' in str(e).lower():
                print('mentors table already exists')
            else:
                print(f'Error creating table: {e}')
        
        # Add indexes
        try:
            conn.execute(text('CREATE INDEX IF NOT EXISTS ix_mentors_user_id ON mentors(user_id)'))
            conn.execute(text('CREATE INDEX IF NOT EXISTS ix_mentors_name ON mentors(name)'))
            conn.execute(text('CREATE INDEX IF NOT EXISTS ix_mentors_specialization ON mentors(specialization)'))
            print('Added indexes')
        except Exception as e:
            print(f'Note on indexes: {e}')
        
        conn.commit()
        print('Migration completed: mentors table created')

def rollback():
    with engine.connect() as conn:
        try:
            conn.execute(text('DROP TABLE IF EXISTS mentors CASCADE'))
            print('Dropped mentors table')
        except Exception as e:
            print(f'Rollback error: {e}')
        conn.commit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
