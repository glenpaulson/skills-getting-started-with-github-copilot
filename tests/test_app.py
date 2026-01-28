"""
Tests for the FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Test getting activities endpoint"""
    
    def test_get_activities_returns_200(self):
        """Test that /activities endpoint returns 200 status"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that /activities endpoint returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_activities_have_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity in activities.items():
            for field in required_fields:
                assert field in activity, f"Activity {activity_name} missing field {field}"
    
    def test_activities_not_empty(self):
        """Test that activities list is not empty"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) > 0


class TestSignupForActivity:
    """Test signup endpoint"""
    
    def test_signup_valid_activity_and_email(self):
        """Test successful signup"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=newemail@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_nonexistent_activity(self):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_email(self):
        """Test signup with email already registered"""
        activity_name = "Tennis Club"
        email = "james@mergington.edu"  # Already registered
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_message_contains_email(self):
        """Test that success message contains the email"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test123@mergington.edu"
        )
        assert "test123@mergington.edu" in response.json()["message"]


class TestUnregisterFromActivity:
    """Test unregister endpoint"""
    
    def test_unregister_valid_activity_and_email(self):
        """Test successful unregister"""
        # First, sign up
        client.post(
            "/activities/Drama%20Club/signup?email=tempstudent@mergington.edu"
        )
        
        # Then unregister
        response = client.post(
            "/activities/Drama%20Club/unregister?email=tempstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_nonexistent_activity(self):
        """Test unregister from activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_not_registered_email(self):
        """Test unregister email not in activity"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_removes_from_participants(self):
        """Test that unregister actually removes the participant"""
        # First, sign up
        email = "tempemail2@mergington.edu"
        client.post(
            f"/activities/Art%20Studio/signup?email={email}"
        )
        
        # Verify they're signed up
        response = client.get("/activities")
        assert email in response.json()["Art Studio"]["participants"]
        
        # Unregister
        client.post(
            f"/activities/Art%20Studio/unregister?email={email}"
        )
        
        # Verify they're removed
        response = client.get("/activities")
        assert email not in response.json()["Art Studio"]["participants"]


class TestRoot:
    """Test root endpoint"""
    
    def test_root_redirect(self):
        """Test that root endpoint redirects"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]
