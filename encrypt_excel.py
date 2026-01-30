import pandas as pd
from werkzeug.security import generate_password_hash

EXCEL_FILE = "users_2026.xlsx"

# 엑셀 불러오기
df = pd.read_excel(EXCEL_FILE)

def encrypt_if_needed(pw):
    pw = str(pw)

    # 이미 암호화된 경우 → 그대로 유지
    if pw.startswith("scrypt:32768:8:1"):
        return pw

    # 평문인 경우만 암호화
    return generate_password_hash(pw)

# password 컬럼 안전하게 암호화
df["password"] = df["password"].apply(encrypt_if_needed)

# 다시 저장
df.to_excel(EXCEL_FILE, index=False)

print("✅ 암호화 완료 (이미 암호화된 값은 건너뜀)")
