# Secure File Sharing Web App

A minimal, secure file sharing web application built with Flask.  
Files are encrypted client-side with a user-provided password using AES-256-CBC.  
No user accounts or database required—just per-file passwords.

---

## Features

- **Secure Upload:**  
  Files are encrypted with AES-256-CBC using a key derived from a password you provide at upload time (PBKDF2-HMAC-SHA256 with random salt).
- **Per-File Passwords:**  
  Each file is encrypted with its own password. Only users with the correct password can decrypt and download.
- **No Database:**  
  Metadata (salt for each file) is stored in a simple JSON file.
- **Minimal UI:**  
  Clean, responsive interface for uploading and downloading files.
- **Key Generation:**  
  Includes a `key.py` script to generate secure random keys if needed.

---

## How It Works

### Encryption Flow

1. **Upload:**
    - User selects a file and enters a password.
    - A random salt and IV are generated.
    - A 256-bit key is derived from the password and salt using PBKDF2-HMAC-SHA256.
    - The file is padded and encrypted with AES-256-CBC.
    - The encrypted file is saved as:  
      `[salt][iv][ciphertext]` in the `encrypted_files/` folder.
    - The salt is also stored in `encrypted_files/meta.json` for key derivation during download.

2. **Download:**
    - User enters the password for the file.
    - The app retrieves the salt and IV, derives the key, and attempts to decrypt.
    - If the password is correct, the file is streamed back as a download.
    - If the password is wrong, a clear error message is shown.

### Key Management

- **Per-file password:**  
  The encryption key is never stored—it's derived from the password and salt at runtime.
- **Salt:**  
  A unique random salt is generated for each file and stored with the file and in metadata.
- **IV:**  
  A random IV is generated for each encryption and prepended to the ciphertext.

### Security Decisions

- **PBKDF2:**  
  Uses PBKDF2-HMAC-SHA256 with a high iteration count for strong key derivation.
- **AES-256-CBC:**  
  Industry-standard symmetric encryption.
- **No plaintext storage:**  
  Only encrypted files and salts are stored.
- **No user accounts:**  
  Simpler attack surface; security is per-file via password.
- **Filename sanitization:**  
  Uses `secure_filename()` to prevent path traversal and unsafe filenames.
- **File size and extension checks:**  
  (Add as needed for your deployment.)

---

## Setup & Usage

### 1. Install dependencies

```bash
pip install flask pycryptodome
```

### 2. Generate a Flask secret key (optional)

You can use the provided `key.py` to generate a random key for Flask session security:

```python
# key.py
import secrets
print(secrets.token_hex(32))
```

Set this as `FLASK_SECRET_KEY` in your environment or `.env` file.

### 3. Run the app

```bash
python app.py
```

Visit [http://localhost:5000/](http://localhost:5000/) in your browser.

### 4. Upload & Download

- **Upload:**  
  Select a file and enter a password. The file is encrypted and stored.
- **Download:**  
  Enter the password you used to encrypt the file. If correct, the file is decrypted and downloaded.

---

## File Structure

```
project/
│
├── app.py
├── key.py
├── encrypted_files/
│   ├── meta.json
│   └── *.enc
├── templates/
│   └── index.html
└── README.md
```

---

## Testing File Integrity

You can test upload/download integrity by comparing file hashes:

```bash
# Upload a file (via web UI)
# Download the file (via web UI)
sha256sum original_file
sha256sum downloaded_file
# The hashes should match if the password was correct
```

---

## Notes

- **Passwords are never stored.** If you forget the password for a file, it cannot be recovered.
- **This app is for demonstration/educational use.** For production, add HTTPS, file size/type restrictions, and further hardening.

---
## Future Scope
- Move encryption and decryption to the client side so the server never sees plaintext data or encryption keys.
- Implement true end-to-end encrypted file sharing, allowing files to be shared securely using passwords or public keys.
- Extend the system to support secure, encrypted text messaging using the same encryption model.
- Improve key management by introducing asymmetric encryption for secure key exchange and access control.
- Enhance scalability and usability by adding better UI, metadata storage, and basic security hardening (limits, validations, HTTPS).

