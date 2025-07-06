from flask import Flask, request, send_from_directory, render_template, jsonify
import os
import socket
import qrcode
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'shared_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    finally:
        s.close()

# STEP 1: Generate access URL
host_ip = get_local_ip()
access_url = f"http://{host_ip}:5000"

# STEP 2: Create QR code with timestamp (avoid cache)
qr_filename = f"qr_{int(time.time())}.png"
qr_path = os.path.join('static', qr_filename)
qr = qrcode.make(access_url)
qr.save(qr_path)

@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    file_info = []
    for f in files:
        path = os.path.join(UPLOAD_FOLDER, f)
        size = os.path.getsize(path)
        file_info.append({'name': f, 'size': round(size / 1024, 2)})
    return render_template('index.html', files=file_info, qr_filename=qr_filename, ip_address=access_url)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return jsonify({'message': 'Upload successful'})
    return jsonify({'message': 'Upload failed'}), 400

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    print(f"Server running at: {access_url}")
    app.run(host='0.0.0.0', port=5000)
