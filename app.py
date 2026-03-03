from flask import Flask, request, send_from_directory, render_template, jsonify
import os
import socket
import qrcode
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'shared_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# 🔹 Get Local IP Address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    finally:
        s.close()

# 🔹 Format File Size Automatically
def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{round(size_bytes / 1024, 2)} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{round(size_bytes / (1024 * 1024), 2)} MB"
    else:
        return f"{round(size_bytes / (1024 * 1024 * 1024), 2)} GB"

# 🔹 Generate QR Code
access_url = f"http://{get_local_ip()}:5000"
qr_path = os.path.join('static', 'qr.png')
qr = qrcode.make(access_url)
qr.save(qr_path)

@app.route('/')
def index():
    files = []

    for f in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, f)
        size = format_size(os.path.getsize(path))
        upload_time = datetime.fromtimestamp(
            os.path.getmtime(path)
        ).strftime('%d-%m-%Y %H:%M')

        files.append({
            'name': f,
            'size': size,
            'time': upload_time
        })

    # Sort latest first
    files.sort(key=lambda x: x['time'], reverse=True)

    return render_template(
        'index.html',
        files=files,
        ip_address=access_url,
        qr_image='qr.png'
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
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    return jsonify({'status': 'deleted'})

if __name__ == '__main__':
    app.run()