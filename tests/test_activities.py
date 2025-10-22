from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep-ish copy of original participants so tests can mutate safely
    original = {
        name: {**data, "participants": list(data.get("participants", []))}
        for name, data in activities.items()
    }
    yield
    # restore
    for name in activities:
        activities[name]["participants"] = list(original[name]["participants"])


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    client = TestClient(app)

    email = "pytest_user@mergington.edu"
    activity = "Chess Club"

    # ensure not present initially
    assert email not in activities[activity]["participants"]

    # signup
    signup = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup.status_code == 200
    assert email in activities[activity]["participants"]

    # signup twice should fail
    signup2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup2.status_code == 400

    # unregister
    unreg = client.post(f"/activities/{activity}/unregister?email={email}")
    assert unreg.status_code == 200
    assert email not in activities[activity]["participants"]

    # unregister again should fail
    unreg2 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert unreg2.status_code == 400
