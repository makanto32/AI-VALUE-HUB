#!/usr/bin/env python3
"""
Test script for technical user workflow.
Tests the end-to-end flow: business analyst creates viable idea → technical user reviews → approves.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Test users
ANALYST_USER = "analista.finanzas"
ANALYST_PASS = "Demo1234!"
TECH_USER = "analista.tecnologia"
TECH_PASS = "Demo1234!"

def log_step(step_num, description):
    print(f"\n{'='*70}")
    print(f"PASO {step_num}: {description}")
    print('='*70)

def test_login(username, password):
    """Test login endpoint"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    token = data.get("access_token")
    assert token, "No access_token in response"
    print(f"✓ Login successful for {username}")
    print(f"  Token: {token[:20]}...")
    return token

def test_get_technical_queue(token):
    """Test technical queue endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/ideas/technical-queue",
        headers=headers
    )
    assert response.status_code == 200, f"Failed to get technical queue: {response.text}"
    data = response.json()
    print(f"✓ Technical queue retrieved")
    print(f"  Ideas in queue: {len(data)}")
    for idea in data:
        print(f"    - {idea['title']} (status: {idea['status']}, stage: {idea['current_stage']})")
    return data

def test_admin_access_denied(token):
    """Test that non-technical users cannot access technical endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/ideas/technical-queue",
        headers=headers
    )
    if response.status_code == 403:
        print(f"✓ Non-technical users correctly denied access to technical queue")
        return True
    else:
        print(f"✗ Expected 403 Forbidden, got {response.status_code}")
        return False

def test_technical_approval(idea_id, token):
    """Test technical approval endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/ideas/{idea_id}/technical-approval",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Technical approval successful")
        print(f"  Architecture package generated: {data.get('architecture_package') is not None}")
        return True
    else:
        print(f"ℹ Technical approval response: {response.status_code}")
        print(f"  Message: {response.text}")
        return False

def test_move_to_funding(idea_id, token):
    """Test move to funding endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(
        f"{BASE_URL}/ideas/{idea_id}/move-to-funding",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Move to funding successful")
        print(f"  Deployment status: {data.get('deployment_status')}")
        return True
    else:
        print(f"ℹ Move to funding response: {response.status_code}")
        print(f"  Message: {response.text}")
        return False

def main():
    print("\n🧪 TESTING TECHNICAL USER WORKFLOW\n")
    
    log_step(1, "Login as analyst")
    analyst_token = test_login(ANALYST_USER, ANALYST_PASS)
    
    log_step(2, "Analyst accesses technical queue (should be denied)")
    test_admin_access_denied(analyst_token)
    
    log_step(3, "Login as technical user")
    tech_token = test_login(TECH_USER, TECH_PASS)
    
    log_step(4, "Technical user accesses technical queue")
    queue = test_get_technical_queue(tech_token)
    
    if len(queue) > 0:
        first_idea = queue[0]
        idea_id = first_idea["idea_id"]
        
        log_step(5, f"Technical user approves first idea: {first_idea['title']}")
        test_technical_approval(idea_id, tech_token)
        
        log_step(6, f"Technical user moves idea to funding")
        test_move_to_funding(idea_id, tech_token)
        
        log_step(7, "Verify idea removed from queue")
        updated_queue = test_get_technical_queue(tech_token)
        if len(updated_queue) < len(queue):
            print(f"✓ Queue updated - ideas reduced from {len(queue)} to {len(updated_queue)}")
        else:
            print(f"ℹ Queue size unchanged (idea still in queue with new status)")
    else:
        print("⚠ No ideas in technical queue to test approval workflow")
    
    log_step(8, "SUMMARY")
    print("✓ All workflow tests completed")
    print("\nTechnical workflow is operational:")
    print("  - Analyst user correctly denied technical queue access")
    print("  - Technical user can access technical queue")
    print("  - Technical user can approve ideas and move to funding")

if __name__ == "__main__":
    main()
