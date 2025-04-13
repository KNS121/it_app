from app.auth import get_password_hash

hash = get_password_hash('aaa')

print(hash)