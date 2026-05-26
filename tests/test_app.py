from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities_state():
    """Keep tests isolated because the app stores data in memory."""
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


def test_get_activities_returns_activity_data():
    # Arrange

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant_to_activity():
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    result = response.json()

    # Assert
    assert response.status_code == 400
    assert result["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_unknown_activity():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/Unknown%20Club/signup?email={email}")
    result = response.json()

    # Assert
    assert response.status_code == 404
    assert result["detail"] == "Activity not found"


def test_unregister_removes_participant_from_activity():
    # Arrange
    email = "alex@mergington.edu"

    # Act
    response = client.delete(f"/activities/Basketball%20Team/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities["Basketball Team"]["participants"]


def test_unregister_returns_404_when_participant_not_found():
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/Basketball%20Team/signup?email={email}"
    )
    result = response.json()

    # Assert
    assert response.status_code == 404
    assert result["detail"] == "Student is not signed up for this activity"
