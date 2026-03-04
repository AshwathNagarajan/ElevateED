"""
Password reset script for test users.
Run this from the backend directory: python reset_test_passwords.py
"""

from database import SessionLocal
from models.user import User
from services.auth import hash_password

# Default test passwords by role
DEFAULT_PASSWORDS = {
    "admin": "dharsini@3137",
    "mentor": "mentor123",
    "student": "student123"
}

def reset_all_test_passwords():
    """Reset all test user passwords to their defaults"""
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        print(f"Found {len(users)} users in database")
        print("-" * 50)
        
        for user in users:
            role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            default_password = DEFAULT_PASSWORDS.get(role, "student123")
            
            user.hashed_password = hash_password(default_password)
            print(f"Reset password for: {user.email} (role: {role})")
        
        db.commit()
        print("-" * 50)
        print("All passwords have been reset to defaults!")
        print()
        print("Default passwords:")
        for role, password in DEFAULT_PASSWORDS.items():
            print(f"  {role}: {password}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

def reset_single_user_password(email: str, new_password: str):
    """Reset password for a specific user"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"User not found: {email}")
            return False
        
        user.hashed_password = hash_password(new_password)
        db.commit()
        
        print(f"Password reset successfully for: {email}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def list_all_users():
    """List all users in the database"""
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        print(f"\n{'='*60}")
        print(f"{'Full Name':<25} {'Email':<35} {'Role':<10}")
        print(f"{'='*60}")
        
        for user in users:
            role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            print(f"{user.full_name:<25} {user.email:<35} {role:<10}")
        
        print(f"{'='*60}")
        print(f"Total: {len(users)} users")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_all_users()
        elif command == "reset-all":
            reset_all_test_passwords()
        elif command == "reset" and len(sys.argv) >= 4:
            email = sys.argv[2]
            password = sys.argv[3]
            reset_single_user_password(email, password)
        else:
            print("Usage:")
            print("  python reset_test_passwords.py list              - List all users")
            print("  python reset_test_passwords.py reset-all         - Reset all passwords to defaults")
            print("  python reset_test_passwords.py reset EMAIL PASS  - Reset specific user password")
    else:
        # Default action: reset all passwords
        reset_all_test_passwords()
