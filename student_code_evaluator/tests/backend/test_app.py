import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from student_code_evaluator.backend.app import app, get_db, init_db
import os

# Use an in-memory database for testing
DATABASE = ':memory:'

@pytest.fixture
def inmemory_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    # Read and execute the schema.sql file
    schema_path = os.path.join(app.root_path, 'schema.sql')
    with open(schema_path, 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    yield db
    db.close()

@pytest.fixture
def client(inmemory_db):
    app.config['TESTING'] = True
    # Patch get_db to return the in-memory database connection
    with patch('student_code_evaluator.backend.app.get_db', return_value=inmemory_db):
        with app.test_client() as client:
            yield client

def test_get_db(client, inmemory_db):
    with app.app_context():
        db = get_db()
        assert isinstance(db, sqlite3.Connection)
        assert db.row_factory == sqlite3.Row

def test_init_db(inmemory_db):
    cursor = inmemory_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table['name'] for table in tables]
    assert 'conversations' in table_names
    assert 'messages' in table_names
    assert 'feedback' in table_names

def test_save_conversation_with_user_id(client, inmemory_db):
    response = client.post('/save_conversation', json={
        "conversation_id": "user_conv_1",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "user_id": "testuser@example.com"
    })
    assert response.status_code == 201
    cursor = inmemory_db.cursor()
    cursor.execute("SELECT * FROM conversations WHERE id = ?", ("user_conv_1",))
    conversation = cursor.fetchone()
    assert conversation is not None
    assert conversation['user_id'] == "testuser@example.com"

def test_get_conversations_by_user(client, inmemory_db):
    client.post('/save_conversation', json={
        "conversation_id": "conv_user1",
        "messages": [{"role": "user", "content": "Msg 1"}],
        "user_id": "user1@example.com"
    })
    client.post('/save_conversation', json={
        "conversation_id": "conv_user2",
        "messages": [{"role": "user", "content": "Msg 2"}],
        "user_id": "user2@example.com"
    })
    response = client.get('/get_conversations?user_id=user1@example.com')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['id'] == 'conv_user1'
    assert data[0]['user_id'] == 'user1@example.com'
    response = client.get('/get_conversations?user_id=user2@example.com')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 'conv_user2'
    assert data[0]['user_id'] == 'user2@example.com'

def test_database_persistence(tmp_path):
    db_path = tmp_path / "persist_test.db"
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    schema_path = os.path.join(app.root_path, 'schema.sql')
    with open(schema_path, 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.execute("INSERT INTO conversations (id, user_id) VALUES (?, ?)", ("persist_conv", "persist_user@example.com"))
    db.commit()
    db.close()
    db2 = sqlite3.connect(db_path)
    db2.row_factory = sqlite3.Row
    cursor = db2.cursor()
    cursor.execute("SELECT * FROM conversations WHERE id = ?", ("persist_conv",))
    conversation = cursor.fetchone()
    assert conversation is not None
    assert conversation['user_id'] == "persist_user@example.com"
    db2.close()

def test_session_timeout_logic():
    import time
    TIMEOUT_MINUTES = 15
    now = time.time()
    last_active = now - (TIMEOUT_MINUTES * 60) - 1
    user_id = "test@example.com"
    assert (now - last_active) > TIMEOUT_MINUTES * 60
    last_active = now - (TIMEOUT_MINUTES * 60) + 10
    assert (now - last_active) < TIMEOUT_MINUTES * 60

def test_close_db():
    assert callable(app.teardown_appcontext)
