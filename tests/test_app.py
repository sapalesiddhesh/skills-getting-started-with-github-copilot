import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_payload():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    encoded_name = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    encoded_name = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant():
    # Arrange
    activity_name = "Programming Class"
    email = activities[activity_name]["participants"][0]
    encoded_name = quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{encoded_name}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "missing@mergington.edu"
    encoded_name = quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{encoded_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_signup_invalid_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    encoded_name = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_invalid_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    encoded_name = quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{encoded_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
