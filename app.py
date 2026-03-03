from flask import Flask, request, send_from_directory, render_template, jsonify, redirect, session
import os
import socket
import sqlite3
import qrcode
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = 'shared_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ("admin", "admin123", "admin"))
    except:
        pass

    conn.commit()
    conn.close()

init_db()

# ================= HELPERS =================
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    finally:
        s.close()

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{round(size_bytes / 1024, 2)} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{round(size_bytes / (1024 * 1024), 2)} MB"
    else:
        return f"{round(size_bytes / (1024 * 1024 * 1024), 2)} GB"

# ================= QR GENERATION =================
access_url = f"http://{get_local_ip()}:5000"
qr_path = os.path.join('static', 'qr.png')
qr = qrcode.make(access_url)
qr.save(qr_path)

# ================= AUTH =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username
            session['role'] = user[3]
            return redirect('/')
        else:
            return "Invalid Credentials"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ================= MAIN =================
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')

    files = []
    total_size = 0

    for f in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, f)
        size_bytes = os.path.getsize(path)
        total_size += size_bytes

        files.append({
            'name': f,
            'size': format_size(size_bytes),
            'time': datetime.fromtimestamp(
                os.path.getmtime(path)
            ).strftime('%d-%m-%Y %H:%M')
        })

    files.sort(key=lambda x: x['time'], reverse=True)

    max_limit = 5 * 1024 * 1024 * 1024
    usage_percent = round((total_size / max_limit) * 100, 2)

    return render_template(
        'index.html',
        files=files,
        usage=usage_percent,
        ip_address=access_url,
        qr_image='qr.png',
        role=session.get('role')
    )

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return jsonify({'status': 'success'})
    return jsonify({'status': 'fail'}), 400

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete(filename):
    if session.get('role') != 'admin':
        return "Access Denied"
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    return jsonify({'status': 'deleted'})

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return "Access Denied"

    total_files = len(os.listdir(UPLOAD_FOLDER))
    return f"<h1>Admin Dashboard</h1><p>Total Files: {total_files}</p><a href='/'>Back</a>"

if __name__ == '__main__':
    app.run()