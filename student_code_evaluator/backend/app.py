from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'chat_history.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # Access columns by name
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

from flask import g

@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    data = request.json
    conversation_id = data.get('conversation_id')
    messages = data.get('messages') # List of {"role": "...", "content": "..."}

    if not conversation_id or not messages:
        return jsonify({"error": "Missing conversation_id or messages"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        # Check if conversation already exists, if not, insert it
        cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
        existing_conversation = cursor.fetchone()
        if existing_conversation is None:
            cursor.execute("INSERT INTO conversations (id) VALUES (?)", (conversation_id,))

        # Insert messages
        for message in messages:
            cursor.execute("INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                           (conversation_id, message['role'], message['content']))

        db.commit()
        return jsonify({"success": True}), 201
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    data = request.json
    conversation_id = data.get('conversation_id')
    feedback_text = data.get('feedback')

    if not conversation_id or not feedback_text:
        return jsonify({"error": "Missing conversation_id or feedback"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        # Check if the conversation exists
        cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
        existing_conversation = cursor.fetchone()
        if existing_conversation is None:
            return jsonify({"error": f"Conversation with ID {conversation_id} not found"}), 404

        # Insert feedback, linking to the conversation
        cursor.execute("INSERT INTO feedback (conversation_id, feedback_text) VALUES (?, ?)",
                       (conversation_id, feedback_text))

        db.commit()
        return jsonify({"success": True}), 201
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/get_conversations', methods=['GET'])
def get_conversations():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT * FROM conversations ORDER BY timestamp DESC")
        conversations = cursor.fetchall()

        conversations_list = []
        for conversation in conversations:
            conversation_data = dict(conversation)
            
            # Get messages for the conversation
            cursor.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", (conversation['id'],))
            messages = cursor.fetchall()
            conversation_data['messages'] = [dict(message) for message in messages]

            # Get feedback for the conversation
            cursor.execute("SELECT * FROM feedback WHERE conversation_id = ? ORDER BY timestamp ASC", (conversation['id'],))
            feedback = cursor.fetchall()
            conversation_data['feedback'] = [dict(f) for f in feedback]

            conversations_list.append(conversation_data)

        return jsonify(conversations_list), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


if __name__ == '__main__':
    # In a real deployment, you'd use a production-ready server like Gunicorn or uWSGI
    # For simple local testing:
    # init_db() # Uncomment to initialize db on first run if not using flask initdb
    app.run(debug=True, port=5000) # Run on a different port than Streamlit
