from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestGuidancePlan:
    def test_guidance_plan_for_new_student(self, client: TestClient, student_token: str):
        response = client.get(
            "/api/recommendations/guidance-plan",
            headers={"Authorization": f"Bearer {student_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "guidance_summary" in data
        assert data["support_level"] in ["light", "medium", "high"]
        assert data["suggested_track"]["track"]
        assert isinstance(data["next_steps"], list)
        assert isinstance(data["recommended_courses"], list)

    def test_guidance_plan_recommends_courses_by_interest(
        self,
        client: TestClient,
        student_token: str,
        test_db: Session,
    ):
        from models.course import Course

        course = Course(
            title="Computer Basics Starter",
            description="A gentle start for digital skills",
            track_type="AI & ML",
            level="Beginner",
        )
        test_db.add(course)
        test_db.commit()

        response = client.get(
            "/api/recommendations/guidance-plan",
            headers={"Authorization": f"Bearer {student_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        course_titles = [item["title"] for item in data["recommended_courses"]]
        assert "Computer Basics Starter" in course_titles
