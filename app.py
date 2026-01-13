from flask import Flask, request, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database helper function to get the current text
def get_current_text():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM paste LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else ""

# Function to either update or insert the new text
def save_text(content):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check if there is already a text in the database
    cursor.execute('SELECT COUNT(*) FROM paste')
    count = cursor.fetchone()[0]

    if count > 0:
        # Update the existing row
        cursor.execute('UPDATE paste SET content = ? WHERE id = 1', (content,))
    else:
        # Insert the first row
        cursor.execute('INSERT INTO paste (id, content) VALUES (1, ?)', (content,))

    conn.commit()
    conn.close()

# Route for the main page
@app.route('/pastebin', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_content = request.form['content']
        if new_content.strip():  # Ensure it's not empty
            save_text(new_content)
            socketio.emit('content_update', {'content': new_content})
        return redirect(url_for('index'))  # Reload the page after submitting

    current_text = get_current_text()
    return render_template('index.html', current_text=current_text)

# WebSocket event to get current content when client connects
@socketio.on('connect')
def handle_connect():
    current_text = get_current_text()
    emit('content_update', {'content': current_text})

if __name__ == '__main__':
    socketio.run(app, debug=False, port=8000, allow_unsafe_werkzeug=True)
