from flask import Flask, render_template, request, redirect, url_for, send_file, abort, flash
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from io import BytesIO
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(16))
STORAGE_FOLDER = 'encrypted_files'
META_FILE = os.path.join(STORAGE_FOLDER, 'meta.json')
os.makedirs(STORAGE_FOLDER, exist_ok=True)

PBKDF2_ITER = 200_000
SALT_SIZE = 16
IV_SIZE = 16
KEY_SIZE = 32  # AES-256

# Load or initialize metadata
if os.path.exists(META_FILE):
    with open(META_FILE, 'r') as f:
        file_meta = json.load(f)
else:
    file_meta = {}

def save_meta():
    with open(META_FILE, 'w') as f:
        json.dump(file_meta, f)

@app.route('/', methods=['GET'])
def index():
    files = [f for f in os.listdir(STORAGE_FOLDER) if f.endswith('.enc')]
    error = request.args.get('error')
    return render_template('index.html', files=files, error=error)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files or 'password' not in request.form:
        flash('Missing file or password.')
        return redirect(url_for('index'))
    file = request.files['file']
    password = request.form['password']
    if file.filename == '' or not password:
        flash('No file selected or password missing.')
        return redirect(url_for('index'))
    filename = secure_filename(file.filename)
    data = file.read()
    salt = get_random_bytes(SALT_SIZE)
    iv = get_random_bytes(IV_SIZE)
    key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=PBKDF2_ITER)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len]) * pad_len
    ciphertext = cipher.encrypt(data)
    with open(os.path.join(STORAGE_FOLDER, filename + '.enc'), 'wb') as f:
        f.write(salt + iv + ciphertext)
    file_meta[filename + '.enc'] = {'salt': salt.hex()}
    save_meta()
    flash('File uploaded and encrypted successfully.')
    return redirect(url_for('index'))

@app.route('/download/<filename>', methods=['POST'])
def download(filename):
    enc_filename = secure_filename(filename) + '.enc'
    enc_path = os.path.join(STORAGE_FOLDER, enc_filename)
    password = request.form.get('download_password', '')
    if not os.path.exists(enc_path) or enc_filename not in file_meta:
        abort(404)
    if not password:
        flash('Password required to decrypt.')
        return redirect(url_for('index'))
    with open(enc_path, 'rb') as f:
        salt = f.read(SALT_SIZE)
        iv = f.read(IV_SIZE)
        ciphertext = f.read()
    try:
        key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=PBKDF2_ITER)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = cipher.decrypt(ciphertext)
        pad_len = data[-1]
        if pad_len < 1 or pad_len > 16:
            raise ValueError("Invalid padding")
        data = data[:-pad_len]
    except Exception:
        flash('Wrong password or file corrupted.')
        return redirect(url_for('index', error='wrong_password'))
    return send_file(BytesIO(data), as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)