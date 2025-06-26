import requests
import pytest
import time

# Use the correct port for backend as mapped in docker-compose.yml
BACKEND_URL = "http://127.0.0.1:5001"

# Assuming the backend is running at http://localhost:5000
# In a real integration test setup, you might use a test runner
# that starts and stops the backend server.

# Wait for the backend to be available (optional, but helpful in automated environments)
def wait_for_backend():
    url = f"{BACKEND_URL}/get_conversations" # Use a simple endpoint to check
    retries = 60  # Increased retries
    sleep_time = 5 # Increased sleep time
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Backend is available.")
                return
        except requests.exceptions.ConnectionError as e:
            print(f"Waiting for backend, attempt {i+1}/{retries}... Error: {e}")
            time.sleep(sleep_time)
    pytest.fail("Backend did not become available after multiple retries.")

@pytest.fixture(scope="module", autouse=True)
def setup_backend():
    # In a real scenario, you would start the backend server here
    # and yield, then stop it in a teardown.
    # For this example, we assume the backend is already running.
    wait_for_backend()
    yield
    # In a real scenario, you would stop the backend server here

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Deletes test data before each test run."""
    conversation_id_1 = "integration_test_conv_1"
    conversation_id_2 = "integration_test_conv_2"
    
    # Delete messages
    requests.delete(f"{BACKEND_URL}/delete_messages/{conversation_id_1}")
    requests.delete(f"{BACKEND_URL}/delete_messages/{conversation_id_2}")

    # Delete conversations
    requests.delete(f"{BACKEND_URL}/delete_conversation/{conversation_id_1}")
    requests.delete(f"{BACKEND_URL}/delete_conversation/{conversation_id_2}")


def test_save_and_get_conversation():
    conversation_id = "integration_test_conv_1"
    messages = [
        {"role": "user", "content": "Integration test message 1"},
        {"role": "assistant", "content": "Integration test response 1"}
    ]
    user_id = "integration_user@example.com"
    save_response = requests.post(f"{BACKEND_URL}/save_conversation", json={
        "conversation_id": conversation_id,
        "messages": messages,
        "user_id": user_id
    })
    assert save_response.status_code == 201
    assert save_response.json() == {"success": True}
    get_response = requests.get(f"{BACKEND_URL}/get_conversations?user_id={user_id}")
    assert get_response.status_code == 200
    conversations = get_response.json()
    found_conv = None
    for conv in conversations:
        if conv['id'] == conversation_id:
            found_conv = conv
            break
    assert found_conv is not None
    assert len(found_conv['messages']) == 2
    assert found_conv['messages'][0]['content'] == "Integration test message 1"
    assert found_conv['messages'][1]['content'] == "Integration test response 1"

def test_conversation_tagged_to_user():
    conversation_id = "integration_test_conv_2"
    messages = [
        {"role": "user", "content": "User-specific message"}
    ]
    user_id_1 = "user1@example.com"
    user_id_2 = "user2@example.com"
    requests.post(f"{BACKEND_URL}/save_conversation", json={
        "conversation_id": conversation_id + "_1",
        "messages": messages,
        "user_id": user_id_1
    })
    requests.post(f"{BACKEND_URL}/save_conversation", json={
        "conversation_id": conversation_id + "_2",
        "messages": messages,
        "user_id": user_id_2
    })
    resp1 = requests.get(f"{BACKEND_URL}/get_conversations?user_id={user_id_1}")
    resp2 = requests.get(f"{BACKEND_URL}/get_conversations?user_id={user_id_2}")
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    data1 = resp1.json()
    data2 = resp2.json()
    assert all(conv['user_id'] == user_id_1 for conv in data1)
    assert all(conv['user_id'] == user_id_2 for conv in data2)

# TODO: Add more integration tests as needed
