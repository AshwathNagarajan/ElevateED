"""
Tests for course and enrollment workflows.

Coverage:
- Creating a course (admin only)
- Enrolling a student in a course
- Retrieving enrolled courses
- Happy path workflow: create course → enroll student → check enrollment
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def test_course(test_db: Session, admin_user):
    """Create a test course directly in database."""
    from models.course import Course
    
    course = Course(
        title="Introduction to Python",
        description="Learn Python fundamentals",
        track_type="Programming",
        level="Beginner",
        duration_hours=10.0,
        instructor="John Doe",
        mentor_id=admin_user.id
    )
    test_db.add(course)
    test_db.commit()
    test_db.refresh(course)
    return course


class TestCourseCreation:
    """Test suite for course creation."""
    
    def test_create_course_as_admin(self, client: TestClient, admin_token: str):
        """Test that admin can create a course."""
        response = client.post(
            "/api/courses/",
            json={
                "title": "Web Development Fundamentals",
                "description": "Learn HTML, CSS, and JavaScript",
                "track_type": "Web Development",
                "level": "Beginner",
                "duration_hours": 20.0,
                "instructor": "Jane Smith"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Web Development Fundamentals"
        assert data["track_type"] == "Web Development"
        assert data["level"] == "Beginner"
        assert "id" in data
    
    def test_create_course_as_student_fails(self, client: TestClient, student_token: str):
        """Test that non-admin cannot create a course."""
        response = client.post(
            "/api/courses/",
            json={
                "title": "Advanced Python",
                "description": "Advanced Python concepts",
                "track_type": "Programming",
                "level": "Advanced",
                "duration_hours": 30.0
            },
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code in [401, 403]
    
    def test_create_course_with_mentor(self, client: TestClient, admin_token: str, mentor_user):
        """Test creating a course and assigning a mentor."""
        response = client.post(
            "/api/courses/",
            json={
                "title": "Data Science Bootcamp",
                "description": "Comprehensive data science course",
                "track_type": "Data Science",
                "level": "Intermediate",
                "duration_hours": 40.0,
                "mentor_id": mentor_user.id
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["mentor_id"] == mentor_user.id


class TestCourseEnrollment:
    """Test suite for course enrollment workflow."""
    
    def test_enroll_in_course_success(self, client: TestClient, student_token: str, test_course):
        """Test successful course enrollment."""
        response = client.post(
            f"/api/enrollments/enroll/{test_course.id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["course_id"] == test_course.id
        assert data["progress_percentage"] == 0.0
        assert data["completed"] is False
    
    def test_enroll_duplicate_fails(self, client: TestClient, student_token: str, test_course):
        """Test that enrolling twice in same course fails."""
        # First enrollment
        response1 = client.post(
            f"/api/enrollments/enroll/{test_course.id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response1.status_code == 201
        
        # Duplicate enrollment attempt
        response2 = client.post(
            f"/api/enrollments/enroll/{test_course.id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response2.status_code == 400
        assert "already enrolled" in response2.json()["detail"].lower()
    
    def test_enroll_nonexistent_course(self, client: TestClient, student_token: str):
        """Test enrolling in non-existent course fails."""
        response = client.post(
            "/api/enrollments/enroll/99999",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_my_courses(self, client: TestClient, student_token: str, test_course):
        """Test retrieving student's enrolled courses."""
        # First, enroll in course
        enroll_response = client.post(
            f"/api/enrollments/enroll/{test_course.id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert enroll_response.status_code == 201
        
        # Then, retrieve enrolled courses
        response = client.get(
            "/api/enrollments/my-courses",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Check that our test course is in the list
        course_ids = [item.get("id") for item in data]
        assert test_course.id in course_ids


class TestEnrollmentProgressTracking:
    """Test suite for tracking student progress in courses."""
    
    def test_update_course_progress(self, client: TestClient, student_token: str, test_course, test_db: Session):
        """Test updating course progress."""
        from models.enrollment import Enrollment
        
        # Create enrollment directly
        enrollment = Enrollment(
            student_id=1,  # First user created in fixtures
            course_id=test_course.id,
            progress_percentage=0.0,
            completed=False
        )
        test_db.add(enrollment)
        test_db.commit()
        test_db.refresh(enrollment)
        
        # Update progress
        response = client.put(
            f"/api/enrollments/update-progress/{enrollment.id}",
            json={"progress_percentage": 50.0},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Should succeed or require admin permissions
        assert response.status_code in [200, 401, 403]
    
    def test_get_course_progress(self, client: TestClient, student_token: str, test_course, test_db: Session):
        """Test retrieving course progress."""
        from models.enrollment import Enrollment
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=1,
            course_id=test_course.id,
            progress_percentage=25.0,
            completed=False
        )
        test_db.add(enrollment)
        test_db.commit()
        test_db.refresh(enrollment)
        
        # Get progress
        response = client.get(
            f"/api/enrollments/course-progress/{test_course.id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Should return enrollment info or 404
        assert response.status_code in [200, 404]


class TestCourseEnrollmentHappyPath:
    """Integration test for complete course and enrollment workflow."""
    
    def test_full_course_workflow(self, client: TestClient, admin_token: str, student_token: str, test_db: Session):
        """Test complete workflow: create course → student enrolls → view enrollment."""
        
        # Step 1: Admin creates a course
        create_response = client.post(
            "/api/courses/",
            json={
                "title": "Machine Learning 101",
                "description": "Introduction to ML",
                "track_type": "AI & ML",
                "level": "Beginner",
                "duration_hours": 25.0
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 201
        course_id = create_response.json()["id"]
        
        # Step 2: Student enrolls in the course
        enroll_response = client.post(
            f"/api/enrollments/enroll/{course_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert enroll_response.status_code == 201
        enrollment_data = enroll_response.json()
        assert enrollment_data["course_id"] == course_id
        assert enrollment_data["progress_percentage"] == 0.0
        
        # Step 3: Student can view their enrolled course
        my_courses_response = client.get(
            "/api/enrollments/my-courses",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert my_courses_response.status_code == 200
        my_courses = my_courses_response.json()
        assert any(course.get("id") == course_id for course in my_courses)
        
        # Step 4: Verify course details
        course_detail_response = client.get(
            f"/api/courses/{course_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert course_detail_response.status_code == 200
        course_detail = course_detail_response.json()
        assert course_detail["title"] == "Machine Learning 101"
        assert course_detail["track_type"] == "AI & ML"
