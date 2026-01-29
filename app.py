from flask import Flask, render_template, request, redirect, session, send_from_directory, abort
from werkzeug.security import check_password_hash
import pandas as pd
import os

# --------------------
# Flask 기본 설정
# --------------------
app = Flask(__name__, static_folder=None)
app.secret_key = "very-strong-secret-key-987654321"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_ROOT = os.path.join(BASE_DIR, "pdfs")

# --------------------
# 공통 함수
# --------------------
def load_users(year):
    """
    선택된 연도의 엑셀 파일을 읽는다.
    예: users_2025.xlsx / users_2026.xlsx
    """
    excel_file = os.path.join(BASE_DIR, f"users_{year}.xlsx")

    if not os.path.exists(excel_file):
        raise FileNotFoundError(f"{excel_file} 파일이 존재하지 않습니다.")

    return pd.read_excel(excel_file)


# --------------------
# 로그인 화면
# --------------------
@app.route("/")
def home():
    return render_template("login.html")


# --------------------
# 로그인 처리
# --------------------
@app.route("/login", methods=["POST"])
def login():
    userid = request.form.get("userid")
    password = request.form.get("password")
    year = request.form.get("year")

    df = load_users(year)

    user = df[df["userid"] == userid]

    if user.empty:
        return "신상신고가 완료되지 않았습니다. 회비 납부와 온라인회원신고를 모두 하셔야 신상신고가 완료됩니다."

    hashed_pw = user.iloc[0]["password"]

    if not check_password_hash(hashed_pw, password):
        return "비밀번호가 올바르지 않습니다."

    # 로그인 성공 → 세션 저장
    session["user"] = userid
    session["year"] = year

    return redirect("/print")


# --------------------
# PDF 목록 화면
# --------------------
@app.route("/print")
def print_page():
    if "user" not in session:
        return redirect("/")

    year = session.get("year", "2025")
    userid = session.get("user")

    df = load_users(year)

    user_row = df[df["userid"] == userid]

    if user_row.empty:
        return "사용자 정보를 찾을 수 없습니다."

    user_pdf = user_row.iloc[0]["pdf"]   # 엑셀에 저장된 pdf 이름

    return render_template(
        "print.html",
        pdf_files=[user_pdf],             # ✅ 내 PDF만 전달
        year=year,
        user=userid
    )


# --------------------
# PDF 다운로드 (보안 보호)
# --------------------
@app.route("/pdf/<year>/<filename>")
def serve_pdf(year, filename):
    if "user" not in session:
        abort(403)

    folder = os.path.join(PDF_ROOT, year)

    return send_from_directory(folder, filename, as_attachment=False)


# --------------------
# 로그아웃
# --------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# --------------------
# 서버 실행
# --------------------
if __name__ == "__main__":
    app.run(debug=True)
