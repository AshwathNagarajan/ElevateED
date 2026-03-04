# Dummy Test Users

⚠️ **These credentials are for development/testing only.**
**Do NOT use in production.**

## User Accounts

| Full Name | Email | Password | Role |
|-----------|-------|----------|------|
| Admin | admin@elevated.com | dharsini@3137 | admin |
| John Mentor | mentor@elevated.com | mentor123 | mentor |
| Aarav Patel | aarav.patel@student.elevated.com | student123 | student |
| Bhavna Sharma | bhavna.sharma@student.elevated.com | student123 | student |
| Chirag Verma | chirag.verma@student.elevated.com | student123 | student |
| Divya Gupta | divya.gupta@student.elevated.com | student123 | student |
| Eshan Kumar | eshan.kumar@student.elevated.com | student123 | student |
| Fatima Khan | fatima.khan@student.elevated.com | student123 | student |
| Ganesh Singh | ganesh.singh@student.elevated.com | student123 | student |
| Harsh Malhotra | harsh.malhotra@student.elevated.com | student123 | student |
| Ishita Reddy | ishita.reddy@student.elevated.com | student123 | student |
| Jiya Kapoor | jiya.kapoor@student.elevated.com | student123 | student |
| Karan Nair | karan.nair@student.elevated.com | student123 | student |
| Laxmi Rao | laxmi.rao@student.elevated.com | student123 | student |
| Madhav Desai | madhav.desai@student.elevated.com | student123 | student |
| Neha Menon | neha.menon@student.elevated.com | student123 | student |
| Omkar Tiwari | omkar.tiwari@student.elevated.com | student123 | student |
| Priya Saxena | priya.saxena@student.elevated.com | student123 | student |
| Quentin Das | quentin.das@student.elevated.com | student123 | student |
| Ravi Sharma | ravi.sharma@student.elevated.com | student123 | student |
| Sneha Pandey | sneha.pandey@student.elevated.com | student123 | student |
| Tanvi Joshi | tanvi.joshi@student.elevated.com | student123 | student |
| Umesh Chandra | umesh.chandra@student.elevated.com | student123 | student |
| Vidya Krishnan | vidya.krishnan@student.elevated.com | student123 | student |
| Wasim Ahmed | wasim.ahmed@student.elevated.com | student123 | student |
| Xena Dsouza | xena.dsouza@student.elevated.com | student123 | student |
| Yash Agarwal | yash.agarwal@student.elevated.com | student123 | student |
| Zara Hussain | zara.hussain@student.elevated.com | student123 | student |
| Arjun Mehta | arjun.mehta@student.elevated.com | student123 | student |
| Bhumi Patel | bhumi.patel@student.elevated.com | student123 | student |
| Chetan Yadav | chetan.yadav@student.elevated.com | student123 | student |
| Deepika Nair | deepika.nair@student.elevated.com | student123 | student |
| Ekta Sharma | ekta.sharma@student.elevated.com | student123 | student |
| Farhan Ali | farhan.ali@student.elevated.com | student123 | student |
| Gayatri Pillai | gayatri.pillai@student.elevated.com | student123 | student |
| Hitesh Gupta | hitesh.gupta@student.elevated.com | student123 | student |
| Isha Verma | isha.verma@student.elevated.com | student123 | student |
| Jai Prakash | jai.prakash@student.elevated.com | student123 | student |
| Kavitha Menon | kavitha.menon@student.elevated.com | student123 | student |
| Lokesh Reddy | lokesh.reddy@student.elevated.com | student123 | student |
| Meera Singh | meera.singh@student.elevated.com | student123 | student |
| Naveen Kumar | naveen.kumar@student.elevated.com | student123 | student |
| Ojas Sharma | ojas.sharma@student.elevated.com | student123 | student |
| Pooja Pandey | pooja.pandey@student.elevated.com | student123 | student |
| Qasim Sheikh | qasim.sheikh@student.elevated.com | student123 | student |
| Ritu Malhotra | ritu.malhotra@student.elevated.com | student123 | student |
| Sanjay Tiwari | sanjay.tiwari@student.elevated.com | student123 | student |
| Tara Desai | tara.desai@student.elevated.com | student123 | student |
| Urvashi Kapoor | urvashi.kapoor@student.elevated.com | student123 | student |
| Vikram Joshi | vikram.joshi@student.elevated.com | student123 | student |
| Wriddhiman Sen | wriddhiman.sen@student.elevated.com | student123 | student |
| Yamini Rao | yamini.rao@student.elevated.com | student123 | student |
| Zubin Contractor | zubin.contractor@student.elevated.com | student123 | student |
| Akshay Kulkarni | akshay.kulkarni@student.elevated.com | student123 | student |
| Bindu Raghavan | bindu.raghavan@student.elevated.com | student123 | student |
| Chandni Sethi | chandni.sethi@student.elevated.com | student123 | student |

## Quick Login Credentials

### Admin Access
- **Email:** admin@elevated.com
- **Password:** dharsini@3137

### Mentor Access
- **Email:** mentor@elevated.com
- **Password:** mentor123

### Student Access (any student)
- **Email:** aarav.patel@student.elevated.com
- **Password:** student123

## Password Security Notice

⚠️ **Passwords are securely hashed in the database using bcrypt and cannot be retrieved.**

The passwords listed above are the **original plaintext passwords** used during seeding (defined in `backend/seed_db.py`). They are not stored in plaintext in the database.

## Resetting Passwords for Testing

If you need to reset passwords for testing purposes, use the following script:

```bash
cd backend
python reset_test_passwords.py
```

Alternatively, you can manually reset a user's password using Python:

```python
from database import SessionLocal
from models.user import User
from services.auth import hash_password

db = SessionLocal()
user = db.query(User).filter(User.email == "target@email.com").first()
if user:
    user.hashed_password = hash_password("new_password")
    db.commit()
    print("Password reset successfully!")
db.close()
```

## Email Format

Student emails follow the pattern:
```
{first_name}.{last_name}@student.elevated.com
```

All names are lowercase with spaces replaced by dots.
