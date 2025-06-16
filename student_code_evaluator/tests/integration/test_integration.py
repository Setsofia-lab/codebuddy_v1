import requests
import pytest
import time

# Assuming the backend is running at http://localhost:5000
# In a real integration test setup, you might use a test runner
# that starts and stops the backend server.
BACKEND_URL = "http://127.0.0.1:5000"

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
    
    # Delete feedback first due to foreign key constraints
    requests.delete(f"{BACKEND_URL}/delete_feedback/{conversation_id_1}")
    requests.delete(f"{BACKEND_URL}/delete_feedback/{conversation_id_2}")
    
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

    # Save conversation
    save_response = requests.post(f"{BACKEND_URL}/save_conversation", json={
        "conversation_id": conversation_id,
        "messages": messages
    })
    assert save_response.status_code == 201
    assert save_response.json() == {"success": True}

    # Get conversations and verify the saved one
    get_response = requests.get(f"{BACKEND_URL}/get_conversations")
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
    assert len(found_conv['feedback']) == 0 # No feedback yet

def test_save_feedback_and_get_conversation():
    conversation_id = "integration_test_conv_2"
    messages = [
        {"role": "user", "content": "Integration test message 2"}
    ]
    feedback_text = "This is integration test feedback."

    # Save conversation
    save_conv_response = requests.post(f"{BACKEND_URL}/save_conversation", json={
        "conversation_id": conversation_id,
        "messages": messages
    })
    assert save_conv_response.status_code == 201

    # Save feedback
    save_feedback_response = requests.post(f"{BACKEND_URL}/save_feedback", json={
        "conversation_id": conversation_id,
        "feedback": feedback_text
    })
    assert save_feedback_response.status_code == 201
    assert save_feedback_response.json() == {"success": True}

    # Get conversations and verify the feedback
    get_response = requests.get(f"{BACKEND_URL}/get_conversations")
    assert get_response.status_code == 200
    conversations = get_response.json()

    found_conv = None
    for conv in conversations:
        if conv['id'] == conversation_id:
            found_conv = conv
            break

    assert found_conv is not None
    assert len(found_conv['feedback']) == 1
    assert found_conv['feedback'][0]['feedback_text'] == feedback_text

# TODO: Add more integration tests as needed
