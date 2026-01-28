
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from werkzeug.security import check_password_hash
import pandas as pd
import os
from datetime import datetime

def is_admin():
    return session.get("userid") == "admin"



LOG_FILE = "print_log.csv"

def save_print_log(userid, pdf, ip):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{now},{userid},{pdf},{ip}\n"

    # 파일이 없으면 헤더 생성
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("time,userid,pdf,ip\n")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


app = Flask(__name__, static_folder=None)

app.secret_key = "very-strong-secret-key-987654321"

EXCEL_FILE = "users.xlsx"
PDF_FOLDER = "pdfs"

def load_users():
    return pd.read_excel(EXCEL_FILE)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    userid = request.form["userid"]
    password = request.form["password"]

    df = load_users()
    user = df[df["userid"] == userid]

    if len(user) == 0:
        return "존재하지 않는 사용자입니다"

    hashed_password = user.iloc[0]["password"]
    pdf_file = user.iloc[0]["pdf"]

    if not check_password_hash(hashed_password, password):
        return "비밀번호가 틀렸습니다"

    # 🔐 세션 저장
    session.clear()
    session["userid"] = userid
    session["pdf"] = pdf_file

    print("✅ 세션 생성:", session)

    return redirect(url_for("print_page"))

@app.route("/print")
def print_page():
    if "userid" not in session:
        return redirect(url_for("home"))

    pdf_file = session["pdf"]

    # ✅ 출력 로그 저장
    save_print_log(
        userid=session["userid"],
        pdf=pdf_file,
        ip=request.remote_addr
    )

    return render_template("print.html", pdf_url=f"/pdf/{pdf_file}")

@app.route("/pdf/<filename>")
def serve_pdf(filename):
    print("📂 PDF 접근 요청:", filename)
    print("🔍 현재 세션:", session)

    if "userid" not in session:
        return "접근 권한 없음", 403

    return send_from_directory(PDF_FOLDER, filename)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "userid" not in session:
        return redirect(url_for("home"))

    if not is_admin():
        return "관리자만 접근 가능합니다 ❌", 403

    message = ""

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            message = "파일을 선택하세요"
        elif not allowed_file(file.filename):
            message = "xlsx 파일만 업로드 가능합니다"
        else:
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            # users.xlsx 덮어쓰기
            os.replace(save_path, EXCEL_FILE)
            message = "업로드 완료! 즉시 반영되었습니다 ✅"

    return f"""
        <h2>👑 관리자 페이지</h2>
        <p style='color:green;'>{message}</p>

        <hr>

        <h3>📥 사용자 엑셀 업로드</h3>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">업로드</button>
        </form>

        <hr>

        <h3>📊 출력 로그</h3>
        <a href="/logs" target="_blank">로그 보기</a>

        <hr>

        <a href="/logout">로그아웃</a>
    """
@app.route("/logs")
def view_logs():
    if "userid" not in session or not is_admin():
        return "관리자만 접근 가능합니다", 403

    if not os.path.exists(LOG_FILE):
        return "아직 로그가 없습니다."

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f"<pre>{f.read()}</pre>"



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



