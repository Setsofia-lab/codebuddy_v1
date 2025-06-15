import pytest
from unittest.mock import patch, MagicMock
# import requests_mock
import json
from student_code_evaluator.app.streamlit_app import send_conversation_to_backend, send_feedback_to_backend, generate_llm_response

# Mock the Streamlit sidebar for testing purposes
class MockSidebar:
    def success(self, message):
        print(f"Sidebar Success: {message}")
    def error(self, message):
        print(f"Sidebar Error: {message}")

@pytest.fixture
def mock_streamlit_sidebar():
    with patch('student_code_evaluator.app.streamlit_app.st.sidebar', new=MockSidebar()) as mock_sidebar:
        yield mock_sidebar

def test_send_conversation_to_backend_success(requests_mock, mock_streamlit_sidebar):
    requests_mock.post("http://host.docker.internal:5000/save_conversation", json={"success": True}, status_code=201)
    
    conversation_id = "test_conv_123"
    messages = [{"role": "user", "content": "Test message"}]
    
    send_conversation_to_backend(conversation_id, messages)
    
    assert requests_mock.called
    assert requests_mock.call_count == 1
    history = requests_mock.request_history
    assert history[0].method == 'POST'
    assert history[0].json() == {"conversation_id": conversation_id, "messages": messages}
    # In a real test, you might assert on mock_streamlit_sidebar calls

def test_send_conversation_to_backend_failure(requests_mock, mock_streamlit_sidebar):
    requests_mock.post("http://host.docker.internal:5000/save_conversation", status_code=500)
    
    conversation_id = "test_conv_456"
    messages = [{"role": "user", "content": "Another message"}]
    
    send_conversation_to_backend(conversation_id, messages)
    
    assert requests_mock.called
    assert requests_mock.call_count == 1
    history = requests_mock.request_history
    assert history[0].method == 'POST'
    assert history[0].json() == {"conversation_id": conversation_id, "messages": messages}
    # In a real test, you might assert on mock_streamlit_sidebar calls

def test_send_feedback_to_backend_success(requests_mock, mock_streamlit_sidebar):
    requests_mock.post("http://host.docker.internal:5000/save_feedback", json={"success": True}, status_code=201)

    conversation_id = "test_conv_feedback_123"
    feedback_data = {"q1": "Great", "q2": "Yes"}

    send_feedback_to_backend(conversation_id, feedback_data)

    assert requests_mock.called
    assert requests_mock.call_count == 1
    history = requests_mock.request_history
    assert history[0].method == 'POST'
    assert history[0].json() == {"conversation_id": conversation_id, "feedback": json.dumps(feedback_data)}

def test_send_feedback_to_backend_failure(requests_mock, mock_streamlit_sidebar):
    requests_mock.post("http://host.docker.internal:5000/save_feedback", status_code=400)

    conversation_id = "test_conv_feedback_456"
    feedback_data = {"q1": "Bad"}

    send_feedback_to_backend(conversation_id, feedback_data)

    assert requests_mock.called
    assert requests_mock.call_count == 1
    history = requests_mock.request_history
    assert history[0].method == 'POST'
    assert history[0].json() == {"conversation_id": conversation_id, "feedback": json.dumps(feedback_data)}

@patch('student_code_evaluator.app.streamlit_app.ChatGoogleGenerativeAI')
def test_generate_llm_response_success(mock_chat_google_generative_ai):
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value.content = "LLM response content"
    mock_chat_google_generative_ai.return_value = mock_llm_instance

    messages = [{"role": "user", "content": "User message"}]
    system_prompt = "System prompt."

    response_content = generate_llm_response(messages, mock_llm_instance, system_prompt)

    assert response_content == "LLM response content"
    mock_llm_instance.invoke.assert_called_once()
    # You could add more assertions to check the prompt passed to invoke

@patch('student_code_evaluator.app.streamlit_app.ChatGoogleGenerativeAI')
@patch('student_code_evaluator.app.streamlit_app.st.error')
def test_generate_llm_response_failure(mock_st_error, mock_chat_google_generative_ai):
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.side_effect = Exception("LLM invoke failed")
    mock_chat_google_generative_ai.return_value = mock_llm_instance

    messages = [{"role": "user", "content": "User message"}]
    system_prompt = "System prompt."

    response_content = generate_llm_response(messages, mock_llm_instance, system_prompt)

    assert response_content == "An error occurred during the response generation."
    # In a real test, you might assert on mock_st_error calls

@patch('student_code_evaluator.app.streamlit_app.ChatGoogleGenerativeAI')
def test_get_gemini_llm_success(mock_chat_google_generative_ai):
    mock_llm_instance = MagicMock()
    mock_chat_google_generative_ai.return_value = mock_llm_instance

    llm = generate_llm_response([], mock_llm_instance, "system prompt")
    assert llm is not None
    mock_llm_instance.invoke.assert_called_once_with('system prompt\n\nResponse:')

@patch('student_code_evaluator.app.streamlit_app.ChatGoogleGenerativeAI')
@patch('student_code_evaluator.app.streamlit_app.st.error')
def test_get_gemini_llm_failure(mock_st_error, mock_chat_google_generative_ai):
    mock_chat_google_generative_ai.side_effect = Exception("LLM init failed")

    llm = generate_llm_response([], None, "system prompt") # Pass None for llm to test the error handling within generate_llm_response
    assert llm == "LLM not initialized."
    # In a real test, you might assert on mock_st_error calls
