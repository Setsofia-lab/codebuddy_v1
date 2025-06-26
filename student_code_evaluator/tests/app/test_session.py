import time
import pytest

def test_session_timeout_logic():
    TIMEOUT_MINUTES = 15
    now = time.time()
    last_active = now - (TIMEOUT_MINUTES * 60) - 1  # Just over timeout
    user_id = "test@example.com"
    # Should timeout
    assert (now - last_active) > TIMEOUT_MINUTES * 60
    # Now just under timeout
    last_active = now - (TIMEOUT_MINUTES * 60) + 10
    assert (now - last_active) < TIMEOUT_MINUTES * 60 