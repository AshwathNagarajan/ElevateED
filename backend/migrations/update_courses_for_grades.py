"""
Migration: Update courses for Grade 4-10 students
Removes professional/higher education courses and adds age-appropriate content.

Run from backend directory: python migrations/update_courses_for_grades.py
"""

import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from database import SessionLocal, engine
from models import Course, Module, Lesson, Quiz, QuizSubmission, Enrollment, LessonProgress
import random

# New course data for grades 4-10
NEW_COURSES = [
    {
        "title": "Fun with Numbers - Basic Math",
        "description": "Learn addition, subtraction, multiplication and division through fun activities and games.",
        "track_type": "Mathematics",
        "level": "beginner",
        "duration_hours": 15,
        "instructor": "Mrs. Priya Sharma",
        "modules": [
            {
                "title": "Addition and Subtraction",
                "lessons": [
                    {"title": "Adding Numbers Up to 100", "content": "Learn to add single and double digit numbers with carrying.", "duration": 15},
                    {"title": "Subtraction Made Easy", "content": "Practice subtraction with borrowing using fun examples.", "duration": 15},
                    {"title": "Word Problems", "content": "Solve real-life problems using addition and subtraction.", "duration": 20},
                ]
            },
            {
                "title": "Multiplication Tables",
                "lessons": [
                    {"title": "Times Tables 1-5", "content": "Master multiplication tables from 1 to 5 with tricks.", "duration": 20},
                    {"title": "Times Tables 6-10", "content": "Learn multiplication tables from 6 to 10.", "duration": 20},
                    {"title": "Multiplication Games", "content": "Fun activities to practice multiplication.", "duration": 15},
                ]
            },
        ]
    },
    {
        "title": "Exploring Science - Grade 4-5",
        "description": "Discover the wonders of science through experiments and observations.",
        "track_type": "Science",
        "level": "beginner",
        "duration_hours": 18,
        "instructor": "Mr. Rajesh Kumar",
        "modules": [
            {
                "title": "Living Things Around Us",
                "lessons": [
                    {"title": "Plants and Their Parts", "content": "Learn about roots, stems, leaves, and flowers.", "duration": 20},
                    {"title": "Animal Classification", "content": "Discover mammals, birds, reptiles, fish, and amphibians.", "duration": 20},
                    {"title": "Food Chains", "content": "Understand how energy flows from plants to animals.", "duration": 25},
                ]
            },
        ]
    },
    {
        "title": "English Grammar Basics",
        "description": "Build a strong foundation in English grammar with interactive lessons.",
        "track_type": "English",
        "level": "beginner",
        "duration_hours": 20,
        "instructor": "Ms. Anita Desai",
        "modules": [
            {
                "title": "Parts of Speech",
                "lessons": [
                    {"title": "Nouns and Pronouns", "content": "Identify nouns and use pronouns correctly.", "duration": 20},
                    {"title": "Verbs and Tenses", "content": "Learn action words and when things happen.", "duration": 25},
                    {"title": "Adjectives and Adverbs", "content": "Describe nouns and verbs with descriptive words.", "duration": 20},
                ]
            },
        ]
    },
    {
        "title": "Our India - Social Studies",
        "description": "Learn about India's geography, history, and culture.",
        "track_type": "Social Studies",
        "level": "beginner",
        "duration_hours": 15,
        "instructor": "Mr. Vikram Singh",
        "modules": [
            {
                "title": "India's Geography",
                "lessons": [
                    {"title": "States and Capitals", "content": "Learn all 28 states and 8 union territories.", "duration": 25},
                    {"title": "Rivers of India", "content": "Discover major rivers like Ganga, Yamuna, and Godavari.", "duration": 20},
                    {"title": "Mountains and Plateaus", "content": "Explore the Himalayas and Deccan Plateau.", "duration": 20},
                ]
            },
        ]
    },
    {
        "title": "Introduction to Computers",
        "description": "Learn computer basics, typing, and internet safety.",
        "track_type": "Computer Basics",
        "level": "beginner",
        "duration_hours": 12,
        "instructor": "Ms. Meera Nair",
        "modules": [
            {
                "title": "Computer Parts",
                "lessons": [
                    {"title": "Parts of a Computer", "content": "Identify monitor, keyboard, mouse, and CPU.", "duration": 15},
                    {"title": "Input and Output Devices", "content": "Learn what goes in and comes out of a computer.", "duration": 15},
                    {"title": "Turning On and Shutting Down", "content": "Properly start and close a computer.", "duration": 10},
                ]
            },
        ]
    },
    {
        "title": "Fractions and Decimals",
        "description": "Master fractions, decimals, and percentages for grade 6-7 students.",
        "track_type": "Mathematics",
        "level": "intermediate",
        "duration_hours": 20,
        "instructor": "Mr. Suresh Patel",
        "modules": [
            {
                "title": "Understanding Fractions",
                "lessons": [
                    {"title": "What are Fractions?", "content": "Parts of a whole explained with pizza and cake examples.", "duration": 20},
                    {"title": "Adding Fractions", "content": "Learn to find common denominators.", "duration": 25},
                    {"title": "Multiplying Fractions", "content": "Fraction operations made simple.", "duration": 25},
                ]
            },
        ]
    },
    {
        "title": "Life Science - Grade 6-7",
        "description": "Explore cells, human body systems, and ecosystems.",
        "track_type": "Science",
        "level": "intermediate",
        "duration_hours": 22,
        "instructor": "Dr. Kavitha Rao",
        "modules": [
            {
                "title": "Cells - Building Blocks of Life",
                "lessons": [
                    {"title": "Cell Structure", "content": "Learn about cell membrane, nucleus, and cytoplasm.", "duration": 25},
                    {"title": "Plant vs Animal Cells", "content": "Compare cells with and without cell walls.", "duration": 20},
                    {"title": "Cell Division", "content": "Understanding how cells multiply.", "duration": 25},
                ]
            },
        ]
    },
    {
        "title": "Creative Writing",
        "description": "Develop writing skills through stories, poems, and essays.",
        "track_type": "English",
        "level": "intermediate",
        "duration_hours": 18,
        "instructor": "Mrs. Sunita Krishnan",
        "modules": [
            {
                "title": "Story Writing",
                "lessons": [
                    {"title": "Story Elements", "content": "Characters, setting, plot, and conflict.", "duration": 20},
                    {"title": "Writing Dialogue", "content": "Make characters come alive with speech.", "duration": 25},
                    {"title": "Story Endings", "content": "Write satisfying conclusions.", "duration": 20},
                ]
            },
        ]
    },
    {
        "title": "Ancient Indian History",
        "description": "Journey through India's rich past from Indus Valley to Mughal Empire.",
        "track_type": "Social Studies",
        "level": "intermediate",
        "duration_hours": 20,
        "instructor": "Dr. Ramesh Chandra",
        "modules": [
            {
                "title": "Ancient Civilizations",
                "lessons": [
                    {"title": "Indus Valley Civilization", "content": "Harappa and Mohenjo-daro discoveries.", "duration": 25},
                    {"title": "Vedic Period", "content": "Life during the Vedic age.", "duration": 25},
                    {"title": "Maurya Empire", "content": "Chandragupta and Ashoka the Great.", "duration": 25},
                ]
            },
        ]
    },
    {
        "title": "Scratch Programming",
        "description": "Learn coding basics with fun visual programming blocks.",
        "track_type": "Computer Basics",
        "level": "intermediate",
        "duration_hours": 16,
        "instructor": "Mr. Anil Verma",
        "modules": [
            {
                "title": "Getting Started with Scratch",
                "lessons": [
                    {"title": "The Scratch Interface", "content": "Understand sprites, stage, and blocks.", "duration": 20},
                    {"title": "Motion and Looks", "content": "Make your sprite move and change appearance.", "duration": 20},
                    {"title": "Creating Games", "content": "Build a simple game with events and controls.", "duration": 30},
                ]
            },
        ]
    },
    {
        "title": "Algebra Foundations",
        "description": "Introduction to algebraic expressions, equations and problem solving.",
        "track_type": "Mathematics",
        "level": "advanced",
        "duration_hours": 25,
        "instructor": "Dr. Amit Joshi",
        "modules": [
            {
                "title": "Algebraic Expressions",
                "lessons": [
                    {"title": "Variables and Constants", "content": "Using letters to represent numbers.", "duration": 25},
                    {"title": "Like Terms", "content": "Combine and simplify expressions.", "duration": 25},
                    {"title": "Solving Equations", "content": "Step-by-step equation solving.", "duration": 30},
                ]
            },
        ]
    },
    {
        "title": "Physics for Grade 8-10",
        "description": "Understand forces, motion, energy, and electricity.",
        "track_type": "Science",
        "level": "advanced",
        "duration_hours": 28,
        "instructor": "Mr. Venkat Subramanian",
        "modules": [
            {
                "title": "Motion and Forces",
                "lessons": [
                    {"title": "Speed, Distance, Time", "content": "Calculate motion with formulas.", "duration": 30},
                    {"title": "Newton's Laws", "content": "Three laws of motion explained.", "duration": 35},
                    {"title": "Friction", "content": "Why things slow down.", "duration": 25},
                ]
            },
        ]
    },
    {
        "title": "Chemistry Basics",
        "description": "Learn about atoms, elements, compounds and chemical reactions.",
        "track_type": "Science",
        "level": "advanced",
        "duration_hours": 24,
        "instructor": "Dr. Lakshmi Menon",
        "modules": [
            {
                "title": "Atoms and Elements",
                "lessons": [
                    {"title": "Structure of Atoms", "content": "Protons, neutrons, and electrons.", "duration": 25},
                    {"title": "The Periodic Table", "content": "Understanding elements and their groups.", "duration": 30},
                    {"title": "Chemical Reactions", "content": "Types of reactions and balancing equations.", "duration": 30},
                ]
            },
        ]
    },
    {
        "title": "Geometry and Mensuration",
        "description": "Master shapes, angles, area, and volume calculations.",
        "track_type": "Mathematics",
        "level": "advanced",
        "duration_hours": 22,
        "instructor": "Mrs. Geeta Nair",
        "modules": [
            {
                "title": "Lines and Angles",
                "lessons": [
                    {"title": "Types of Angles", "content": "Acute, obtuse, right, straight angles.", "duration": 20},
                    {"title": "Parallel Lines", "content": "Transversals and angle relationships.", "duration": 25},
                    {"title": "Area and Perimeter", "content": "Calculate area and perimeter of shapes.", "duration": 25},
                ]
            },
        ]
    },
    {
        "title": "Indian Freedom Struggle",
        "description": "Learn about India's journey to independence.",
        "track_type": "Social Studies",
        "level": "advanced",
        "duration_hours": 18,
        "instructor": "Dr. K.N. Rao",
        "modules": [
            {
                "title": "Path to Freedom",
                "lessons": [
                    {"title": "First War of Independence 1857", "content": "The sepoy mutiny and its impact.", "duration": 25},
                    {"title": "Gandhi's Leadership", "content": "Non-Cooperation and Salt March.", "duration": 25},
                    {"title": "Independence and Partition", "content": "August 15, 1947 and building a nation.", "duration": 30},
                ]
            },
        ]
    },
    {
        "title": "Python for Kids",
        "description": "Learn real coding with Python through fun projects and games.",
        "track_type": "Computer Basics",
        "level": "advanced",
        "duration_hours": 24,
        "instructor": "Mr. Karthik Iyer",
        "modules": [
            {
                "title": "Python Basics",
                "lessons": [
                    {"title": "Hello Python!", "content": "Your first Python program.", "duration": 20},
                    {"title": "Variables and Input", "content": "Store data and get user input.", "duration": 25},
                    {"title": "Making Decisions", "content": "If statements and loops.", "duration": 30},
                ]
            },
        ]
    },
]


def run_migration():
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("MIGRATION: Update Courses for Grades 4-10")
        print("=" * 60)
        
        # Step 1: Count existing data
        old_course_count = db.query(Course).count()
        old_enrollment_count = db.query(Enrollment).count()
        print(f"\nExisting courses: {old_course_count}")
        print(f"Existing enrollments: {old_enrollment_count}")
        
        # Step 2: Delete old courses (cascades to modules, lessons, quizzes)
        print("\nDeleting old professional/higher education courses...")
        
        # Use raw SQL for faster cascade deletion
        db.execute(text("DELETE FROM quiz_submissions"))
        db.execute(text("DELETE FROM quizzes"))
        db.execute(text("DELETE FROM lesson_progress"))
        db.execute(text("DELETE FROM enrollments"))
        db.execute(text("DELETE FROM lessons"))
        db.execute(text("DELETE FROM modules"))
        db.execute(text("DELETE FROM courses"))
        db.commit()
        
        print("Old data cleared.")
        
        # Step 3: Add new grade 4-10 courses
        print(f"\nAdding {len(NEW_COURSES)} new age-appropriate courses...")
        
        from models import Module, Lesson
        
        for course_data in NEW_COURSES:
            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                track_type=course_data["track_type"],
                level=course_data["level"],
                duration_hours=course_data.get("duration_hours", 0),
                instructor=course_data.get("instructor", ""),
                rating=round(random.uniform(4.0, 5.0), 1)
            )
            db.add(course)
            db.flush()
            
            # Create modules
            for module_order, module_data in enumerate(course_data["modules"], 1):
                module = Module(
                    course_id=course.id,
                    title=module_data["title"],
                    order_number=module_order
                )
                db.add(module)
                db.flush()
                
                # Create lessons
                for lesson_order, lesson_data in enumerate(module_data["lessons"], 1):
                    lesson = Lesson(
                        module_id=module.id,
                        title=lesson_data["title"],
                        content=lesson_data["content"],
                        video_url=f"https://youtube.com/watch?v=sample{course.id}_{module.id}_{lesson_order}",
                        duration_minutes=lesson_data["duration"]
                    )
                    db.add(lesson)
            
            print(f"  ✓ {course_data['title']}")
        
        db.commit()
        
        # Step 4: Verify
        new_course_count = db.query(Course).count()
        print(f"\n{'=' * 60}")
        print(f"Migration complete!")
        print(f"New courses added: {new_course_count}")
        print(f"{'=' * 60}")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
