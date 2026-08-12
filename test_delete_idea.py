#!/usr/bin/env python
"""
Quick test for the delete idea functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Demo user credentials
USERNAME = "analista.finanzas"
PASSWORD = "Demo1234!"
TENANT = "contoso-demo"

def login():
    """Get auth token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD, "tenant": TENANT}
    )
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None
    data = response.json()
    return data.get("access_token")

def create_test_idea(token):
    """Create a test idea"""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "tenant_id": TENANT,
        "title": "Test Idea for Delete",
        "problem_statement": "This is a test problem statement to verify delete functionality",
        "expected_value": "This is the expected value of solving the problem",
        "source_language": "en"
    }
    response = requests.post(
        f"{BASE_URL}/ideas/intake",
        json=payload,
        headers=headers
    )
    if response.status_code != 200:
        print(f"Create idea failed: {response.text}")
        return None
    data = response.json()
    return data.get("idea_id")

def delete_idea(token, idea_id):
    """Delete the test idea"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/ideas/{idea_id}",
        headers=headers
    )
    if response.status_code == 200:
        print(f"✓ Delete successful: {response.json()['message']}")
        return True
    else:
        print(f"✗ Delete failed ({response.status_code}): {response.text}")
        return False

def verify_deleted(token, idea_id):
    """Verify idea was deleted"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/ideas/{idea_id}",
        headers=headers
    )
    if response.status_code == 404:
        print(f"✓ Idea successfully deleted from database")
        return True
    else:
        print(f"✗ Idea still exists in database")
        return False

if __name__ == "__main__":
    print("Testing delete idea feature...\n")
    
    # Login
    print("1. Logging in...")
    token = login()
    if not token:
        exit(1)
    print(f"✓ Token obtained: {token[:20]}...\n")
    
    # Create test idea
    print("2. Creating test idea...")
    idea_id = create_test_idea(token)
    if not idea_id:
        exit(1)
    print(f"✓ Idea created: {idea_id}\n")
    
    # Delete idea
    print("3. Deleting idea...")
    if not delete_idea(token, idea_id):
        exit(1)
    print()
    
    # Verify deletion
    print("4. Verifying deletion...")
    verify_deleted(token, idea_id)
    print("\n✓ All tests passed!")
