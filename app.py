from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

EXCEL_FILE = "users.xlsx"
PDF_FOLDER = "pdfs"

def load_users():
    df = pd.read_excel(EXCEL_FILE)
    return df

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    userid = request.form["userid"]
    password = request.form["password"]

    df = load_users()

    # userid 일치하는 행 찾기
    user = df[df["userid"] == userid]

    if len(user) == 0:
        return "존재하지 않는 사용자입니다 ❌"

    # 비밀번호 확인
    real_password = str(user.iloc[0]["password"])
    pdf_file = user.iloc[0]["pdf"]

    if password == real_password:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        return send_file(pdf_path)
    else:
        return "비밀번호가 틀렸습니다 ❌"

if __name__ == "__main__":
    app.run(debug=True)
