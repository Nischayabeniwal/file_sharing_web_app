import secrets

# Generate a 32-byte (256-bit) AES key
KEY = secrets.token_bytes(32)
print("Generated AES key (hex):", KEY.hex())
