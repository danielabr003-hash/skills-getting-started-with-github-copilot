from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def reset_activities():
    activities["Chess Club"]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_registering_existing_student_twice_is_rejected():
    reset_activities()

    response = client.post(
        "/activities/Chess Club/signup?email=daniel@mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_registering_new_student_succeeds():
    reset_activities()

    response = client.post(
        "/activities/Chess Club/signup?email=student@mergington.edu"
    )

    assert response.status_code == 200
    assert "student@mergington.edu" in activities["Chess Club"]["participants"]
