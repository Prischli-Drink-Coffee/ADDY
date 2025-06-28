from datetime import datetime, timedelta
import pytest
import random
import string
import hashlib
from fastapi.testclient import TestClient
from src.pipeline.server import app
from src.utils.custom_logging import get_logger
import json

log = get_logger(__name__)
client = TestClient(app)


def generate_random_data(data_type, length=8):
    """Generate random test data based on type"""
    if data_type == "string":
        return ''.join(random.choices(string.ascii_letters, k=length))
    elif data_type == "email":
        return f"{generate_random_data('string')}@example.com"
    elif data_type == "password":
        return hashlib.sha256(generate_random_data('string').encode()).hexdigest()
    elif data_type == "number":
        return random.randint(1, 100)
    elif data_type == "timestamp":
        return datetime.utcnow().isoformat()
    elif data_type == "json":
        return json.dumps({"test": generate_random_data('string')})
    elif data_type == "gender":
        return random.choice(["male", "female", "non-binary", "other"])
    elif data_type == "url":
        return f"https://example.com/{generate_random_data('string')}"
    return None


def api_request(method, url, json_data=None, params=None):
    """Make API request and return response"""
    response = client.request(method, url, json=json_data, params=params)
    log.info(f"API {method} {url} - Status: {response.status_code}")
    return response


def assert_response(response, expected_status, keys=None):
    """Assert response status and check for expected keys"""
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"
    
    if keys:
        response_data = response.json()
        if isinstance(response_data, list):
            for item in response_data:
                for key in keys:
                    assert key in item, f"Key '{key}' not found in response item"
        else:
            for key in keys:
                assert key in response_data, f"Key '{key}' not found in response"
        return response_data
    return None


def create_test_user():
    """Create a test user and return user data"""
    user_data = {
        "email": generate_random_data("email"),
        "password": generate_random_data("password"),
        "first_name": generate_random_data("string", 10),
        "last_activity": generate_random_data("timestamp")
    }
    response = api_request("POST", "/users/", json_data=user_data)
    return assert_response(response, 201, keys=["id"])


def create_test_profile(user_id):
    """Create test profile for user"""
    profile_data = {
        "user_id": user_id,
        "age": generate_random_data("number"),
        "gender": generate_random_data("gender"),
        "interests": generate_random_data("string", 50),
        "bio": generate_random_data("string", 100),
        "profile_photo_url": generate_random_data("url"),
        "location": generate_random_data("string", 15)
    }
    response = api_request("POST", "/profiles/", json_data=profile_data)
    return assert_response(response, 201, keys=["id"])


def create_test_agent(user_id):
    """Create test agent for user"""
    agent_data = {
        "user_id": user_id,
        "personality_data": generate_random_data("json"),
        "learning_status": "ready"
    }
    response = api_request("POST", "/agents/", json_data=agent_data)
    return assert_response(response, 201, keys=["id"])


def create_test_match(user1_id, user2_id):
    """Create test match between users"""
    match_data = {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "match_status": "active"
    }
    response = api_request("POST", "/matches/", json_data=match_data)
    return assert_response(response, 201, keys=["id"])


@pytest.fixture
def test_user():
    """Fixture to create and cleanup test user"""
    user = create_test_user()
    yield user
    api_request("DELETE", f"/users/{user['id']}")


@pytest.fixture
def test_user_with_profile():
    """Fixture to create user with profile"""
    user = create_test_user()
    profile = create_test_profile(user["id"])
    yield {"user": user, "profile": profile}
    api_request("DELETE", f"/users/{user['id']}")


@pytest.fixture
def test_match():
    """Fixture to create two users and a match between them"""
    user1 = create_test_user()
    user2 = create_test_user()
    match = create_test_match(user1["id"], user2["id"])
    yield {"user1": user1, "user2": user2, "match": match}
    api_request("DELETE", f"/users/{user1['id']}")
    api_request("DELETE", f"/users/{user2['id']}")


def test_user_creation():
    """Test user creation endpoint"""
    user_data = {
        "email": generate_random_data("email"),
        "password": generate_random_data("password"),
        "first_name": generate_random_data("string", 10)
    }
    
    # Test successful creation
    response = api_request("POST", "/users/", json_data=user_data)
    user = assert_response(response, 201, keys=["id", "email", "first_name"])
    
    # Test duplicate email
    response = api_request("POST", "/users/", json_data=user_data)
    assert_response(response, 400)
    
    # Cleanup
    api_request("DELETE", f"/users/{user['id']}")


def test_user_login(test_user):
    """Test user login and session creation"""
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    
    # Test successful login
    response = api_request("POST", "/auth/login", json_data=login_data)
    session = assert_response(response, 200, keys=["token", "user_id"])
    
    # Test invalid credentials
    invalid_login = {"email": test_user["email"], "password": "wrong"}
    response = api_request("POST", "/auth/login", json_data=invalid_login)
    assert_response(response, 401)


def test_profile_operations(test_user):
    """Test profile CRUD operations"""
    # Create profile
    profile_data = {
        "user_id": test_user["id"],
        "age": 25,
        "gender": "male",
        "bio": "Test bio"
    }
    response = api_request("POST", "/profiles/", json_data=profile_data)
    profile = assert_response(response, 201, keys=["id", "user_id"])
    
    # Get profile
    response = api_request("GET", f"/profiles/{profile['id']}")
    assert_response(response, 200, keys=["id", "user_id", "age", "gender"])
    
    # Update profile
    update_data = {"bio": "Updated bio"}
    response = api_request("PATCH", f"/profiles/{profile['id']}", json_data=update_data)
    assert_response(response, 200)
    
    # Verify update
    response = api_request("GET", f"/profiles/{profile['id']}")
    updated_profile = assert_response(response, 200)
    assert updated_profile["bio"] == "Updated bio"


def test_match_operations(test_match):
    """Test match operations"""
    match_id = test_match["match"]["id"]
    
    # Get match
    response = api_request("GET", f"/matches/{match_id}")
    assert_response(response, 200, keys=["id", "user1_id", "user2_id"])
    
    # Update match status
    response = api_request("PATCH", f"/matches/{match_id}", 
                         json_data={"match_status": "paused"})
    assert_response(response, 200)
    
    # Verify update
    response = api_request("GET", f"/matches/{match_id}")
    match = assert_response(response, 200)
    assert match["match_status"] == "paused"


def test_agent_operations(test_user):
    """Test agent CRUD operations"""
    # Create agent
    agent_data = {
        "user_id": test_user["id"],
        "personality_data": {"traits": ["friendly", "funny"]},
        "learning_status": "learning"
    }
    response = api_request("POST", "/agents/", json_data=agent_data)
    agent = assert_response(response, 201, keys=["id", "user_id"])
    
    # Get agent
    response = api_request("GET", f"/agents/{agent['id']}")
    assert_response(response, 200, keys=["id", "user_id", "learning_status"])
    
    # Update agent
    response = api_request("PATCH", f"/agents/{agent['id']}", 
                         json_data={"learning_status": "ready"})
    assert_response(response, 200)
    
    # Verify update
    response = api_request("GET", f"/agents/{agent['id']}")
    updated_agent = assert_response(response, 200)
    assert updated_agent["learning_status"] == "ready"


def test_conversation_operations(test_match):
    """Test conversation operations"""
    # Create conversation
    conversation_data = {
        "match_id": test_match["match"]["id"]
    }
    response = api_request("POST", "/conversations/", json_data=conversation_data)
    conversation = assert_response(response, 201, keys=["id", "match_id"])
    
    # Send message
    message_data = {
        "conversation_id": conversation["id"],
        "sender_id": test_match["user1"]["id"],
        "message_text": "Hello!",
        "message_type": "user"
    }
    response = api_request("POST", "/messages/", json_data=message_data)
    message = assert_response(response, 201, keys=["id", "conversation_id"])
    
    # Get conversation messages
    response = api_request("GET", f"/conversations/{conversation['id']}/messages")
    messages = assert_response(response, 200)
    assert len(messages) > 0


def test_simulation_operations(test_user):
    """Test agent simulation operations"""
    # Create two agents
    agent1 = create_test_agent(test_user["id"])
    agent2 = create_test_agent(test_user["id"])
    
    # Create conversation
    conversation_data = {"match_id": None}  # Simplified for test
    response = api_request("POST", "/conversations/", json_data=conversation_data)
    conversation = assert_response(response, 201)
    
    # Create simulation
    simulation_data = {
        "conversation_id": conversation["id"],
        "agent1_id": agent1["id"],
        "agent2_id": agent2["id"],
        "simulation_status": "pending"
    }
    response = api_request("POST", "/simulations/", json_data=simulation_data)
    simulation = assert_response(response, 201, keys=["id", "agent1_id"])
    
    # Add simulation message
    message_data = {
        "simulation_id": simulation["id"],
        "sender_agent_id": agent1["id"],
        "message_text": "Simulated message"
    }
    response = api_request("POST", "/simulation-messages/", json_data=message_data)
    assert_response(response, 201)
    
    # Complete simulation
    response = api_request("PATCH", f"/simulations/{simulation['id']}/complete", 
                         json_data={"compatibility_score": 0.85})
    assert_response(response, 200)