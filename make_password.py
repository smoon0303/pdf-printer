from werkzeug.security import generate_password_hash

password = "1234"   # 원하는 비밀번호
hash = generate_password_hash(password)

print(hash)
