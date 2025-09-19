from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this for production
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Inline HTML template for index.html (served at /)
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Server</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #2c3e50; color: #ecf0f1; }
        #chat { height: 400px; overflow-y: scroll; border: 1px solid #34495e; padding: 10px; margin-bottom: 10px; background: #34495e; }
        #input { width: 70%; padding: 10px; }
        button { padding: 10px 20px; background: #3498db; color: white; border: none; cursor: pointer; }
        button:hover { background: #2980b9; }
        #username { padding: 10px; margin-bottom: 10px; }
        .message { margin: 5px 0; }
        .system { color: #95a5a6; font-style: italic; }
    </style>
</head>
<body>
    <h1>Simple Network Chat (like Discord)</h1>
    <p>Open this file (index.html) on any device and connect to the server URL below.</p>
    <p><strong>Server URL:</strong> wss://your-render-app-name.onrender.com (update after deployment)</p>
    <input type="text" id="username" placeholder="Enter your username" required>
    <div id="chat"></div>
    <input type="text" id="input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMessage();">
    <button onclick="sendMessage();">Send</button>

    <script>
        const socket = io('https://your-render-app-name.onrender.com', { transports: ['websocket'] });  // Update with your Render URL
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');
        const usernameInput = document.getElementById('username');
        let username = '';

        function addMessage(msg, isSystem = false) {
            const div = document.createElement('div');
            div.className = 'message' + (isSystem ? ' system' : '');
            div.innerHTML = msg;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function sendMessage() {
            const msg = input.value.trim();
            if (msg && username) {
                socket.emit('message', { username, msg });
                input.value = '';
            }
        }

        // Wait for username before connecting
        usernameInput.addEventListener('change', () => {
            username = usernameInput.value.trim();
            if (username) {
                socket.connect();
                addMessage(`Connected as ${username}`, true);
            }
        });

        socket.on('connect', () => {
            socket.emit('join', username);
        });

        socket.on('message', (data) => {
            const time = new Date().toLocaleTimeString();
            addMessage(`[${time}] <strong>${data.username}:</strong> ${data.msg}`);
        });

        socket.on('system', (msg) => {
            addMessage(msg, true);
        });

        socket.on('disconnect', () => {
            addMessage('Disconnected from server.', true);
        });

        // Error handling
        socket.on('connect_error', (err) => {
            console.error('SocketIO connect error:', err);  // Log full error to console
            addMessage(`Connection error: ${err.message || 'Unknown websocket error'}`, true);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@socketio.on('join')
def on_join(username):
    join_room('global')  # Simple global room for broadcast
    emit('system', f'{username} joined the chat.', room='global', include_self=False)
    emit('system', f'You joined the chat.', include_self=True)

@socketio.on('message')
def handle_message(data):
    emit('message', data, room='global', include_self=False)
    emit('message', data, include_self=True)  # Echo back to sender

@socketio.on('disconnect')
def on_disconnect():
    emit('system', 'A user left the chat.', room='global')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
