import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture
def restore_participants():
    original_participants = {
        activity_name: activity["participants"].copy()
        for activity_name, activity in activities.items()
    }

    yield

    for activity_name, participants in original_participants.items():
        activities[activity_name]["participants"] = participants


def test_get_activities_returns_activity_details():
    response = client.get("/activities")

    assert response.status_code == 200
    response_data = response.json()
    assert "Chess Club" in response_data
    assert response_data["Chess Club"]["description"]
    assert response_data["Chess Club"]["schedule"]
    assert response_data["Chess Club"]["max_participants"] == 12
    assert isinstance(response_data["Chess Club"]["participants"], list)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_signup_adds_student_and_returns_message(restore_participants):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@mergington.edu for Chess Club"
    }
    assert "student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_student(restore_participants):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "daniel@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email():
    response = client.post("/activities/Chess Club/signup")

    assert response.status_code == 422


def test_unregister_removes_student_and_returns_message(restore_participants):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "daniel@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered daniel@mergington.edu from Chess Club"
    }
    assert "daniel@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_student_who_is_not_signed_up(restore_participants):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up"


def test_unregister_requires_email():
    response = client.delete("/activities/Chess Club/signup")

    assert response.status_code == 422