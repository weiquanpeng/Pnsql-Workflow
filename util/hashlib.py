import hashlib

# 固定盐值
FIXED_SALT = "www.hashlib.com"

def hash_password(password):
    # 将密码和固定盐值组合
    salted_password = password + FIXED_SALT
    # 使用 SHA-256 哈希
    hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
    return hashed_password

def verify_password(password, hashed_password):
    # 对输入的密码进行哈希
    new_hashed_password = hash_password(password)
    # 比较哈希值
    return new_hashed_password == hashed_password