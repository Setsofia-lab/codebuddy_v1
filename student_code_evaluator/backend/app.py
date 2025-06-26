from flask import Flask, request, jsonify, g
import sqlite3
import os

app = Flask(__name__)
DATABASE = './chat_history.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # Ensure the database directory exists
        db_dir = os.path.dirname(DATABASE)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # Access columns by name
            
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with schema."""
    try:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
        if not cursor.fetchone():
            # Read and execute schema
            with open('schema.sql', 'r') as f:
                db.executescript(f.read())
            db.commit()
            print("Database initialized successfully")
        else:
            print("Database already exists")
        
        db.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    data = request.json
    conversation_id = data.get('conversation_id')
    messages = data.get('messages') # List of {"role": "...", "content": "..."}
    user_id = data.get('user_id')

    if not conversation_id or not messages or not user_id:
        return jsonify({"error": "Missing conversation_id, messages, or user_id"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        # Check if conversation already exists, if not, insert it
        cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
        existing_conversation = cursor.fetchone()
        if existing_conversation is None:
            cursor.execute("INSERT INTO conversations (id, user_id) VALUES (?, ?)", (conversation_id, user_id))

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
    user_id = data.get('user_id')

    if not conversation_id or not feedback_text or not user_id:
        return jsonify({"error": "Missing conversation_id, feedback, or user_id"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        # Check if the conversation exists
        cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
        existing_conversation = cursor.fetchone()
        if existing_conversation is None:
            return jsonify({"error": f"Conversation with ID {conversation_id} not found"}), 404

        # Insert feedback, linking to the conversation and user
        cursor.execute("INSERT INTO feedback (conversation_id, user_id, feedback_text) VALUES (?, ?, ?)",
                       (conversation_id, user_id, feedback_text))

        db.commit()
        return jsonify({"success": True}), 201
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/get_conversations', methods=['GET'])
def get_conversations():
    user_id = request.args.get('user_id')
    db = get_db()
    cursor = db.cursor()

    try:
        if user_id:
            cursor.execute("SELECT * FROM conversations WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        else:
            cursor.execute("SELECT * FROM conversations ORDER BY timestamp DESC")
        conversations = cursor.fetchall()

        conversations_list = []
        for conversation in conversations:
            conversation_data = dict(conversation)
            # Get messages for the conversation
            cursor.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", (conversation['id'],))
            messages = cursor.fetchall()
            conversation_data['messages'] = [dict(message) for message in messages]
            conversations_list.append(conversation_data)

        return jsonify(conversations_list), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/delete_conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        db.commit()
        return jsonify({"success": True}), 200
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/delete_messages/<conversation_id>', methods=['DELETE'])
def delete_messages(conversation_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        db.commit()
        return jsonify({"success": True}), 200
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/delete_feedback/<conversation_id>', methods=['DELETE'])
def delete_feedback(conversation_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM feedback WHERE conversation_id = ?", (conversation_id,))
        db.commit()
        return jsonify({"success": True}), 200
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the backend is running."""
    try:
        # Test database connection
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint for the API."""
    return jsonify({
        "message": "CodeBuddy Backend API",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "save_conversation": "/save_conversation",
            "get_conversations": "/get_conversations",
            "save_feedback": "/save_feedback"
        },
        "status": "running"
    }), 200

if __name__ == '__main__':
    # Run in production mode for deployment
    app.run(host='0.0.0.0', port=5000, debug=False)
