"""
Tests for the extracurricular activities API endpoints
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball" in data
    
    def test_get_activities_returns_activity_details(self, client, reset_activities):
        """Test that activity details are returned correctly"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
    
    def test_get_activities_includes_participants(self, client, reset_activities):
        """Test that participant information is included"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that participant is actually added to the activity"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple students can sign up for the same activity"""
        client.post("/activities/Basketball/signup?email=student1@mergington.edu")
        client.post("/activities/Basketball/signup?email=student2@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "student1@mergington.edu" in data["Basketball"]["participants"]
        assert "student2@mergington.edu" in data["Basketball"]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that participant is actually removed from the activity"""
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_nonexistent_participant(self, client, reset_activities):
        """Test unregistering a participant who is not registered"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that an unregistered participant can sign up again"""
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestActivityParticipantCounts:
    """Tests for participant count logic"""
    
    def test_participant_count_increases_on_signup(self, client, reset_activities):
        """Test that participant count increases when someone signs up"""
        response_before = client.get("/activities")
        count_before = len(response_before.json()["Basketball"]["participants"])
        
        client.post("/activities/Basketball/signup?email=newstudent@mergington.edu")
        
        response_after = client.get("/activities")
        count_after = len(response_after.json()["Basketball"]["participants"])
        
        assert count_after == count_before + 1
    
    def test_participant_count_decreases_on_unregister(self, client, reset_activities):
        """Test that participant count decreases when someone unregisters"""
        response_before = client.get("/activities")
        count_before = len(response_before.json()["Chess Club"]["participants"])
        
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        response_after = client.get("/activities")
        count_after = len(response_after.json()["Chess Club"]["participants"])
        
        assert count_after == count_before - 1
