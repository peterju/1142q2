"""
簡易會員系統 (JSON 檔案儲存版)
1142 Web 程式設計 - 第 2 次小考解答
"""
import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
JSON_FILE = "users.json"

# ===== JSON 輔助函式 =====

def load_users():
    """讀取 users.json，如果檔案不存在或錯誤，回傳預設資料"""
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        # 任何錯誤都回傳預設資料（含 admin）
        return {
            "users": [{
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "phone": "0912345678",
                "birthdate": "1990-01-01"
            }]
        }

def save_users(data):
    """將資料寫入 users.json，成功回傳 True，失敗回傳 False"""
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ===== 驗證邏輯 =====

def validate_register(form, users):
    """
    驗證註冊資料：檢查必填、格式、重複
    回傳：(是否成功, 資料或錯誤訊息)
    """
    # 逐一取值並去除空白（簡單直觀）
    username = form.get("username", "").strip()
    email = form.get("email", "").strip()
    password = form.get("password", "").strip()
    phone = form.get("phone", "").strip()
    birthdate = form.get("birthdate", "").strip()

    # 必填檢查
    if not all([username, email, password, birthdate]):
        return False, "帳號、Email、密碼與出生日期為必填欄位"

    # Email 簡易檢查
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Email 格式錯誤"

    # 密碼長度
    if not (6 <= len(password) <= 16):
        return False, "密碼長度需為 6~16 字元"

    # 電話格式（選填，有填才驗）
    if phone and (not phone.isdigit() or len(phone) != 10 or not phone.startswith("09")):
        return False, "電話需為 10 碼數字且以 09 開頭"

    # 重複檢查
    for u in users:
        if u["username"] == username:
            return False, "該帳號已被註冊"
        if u["email"] == email:
            return False, "該 Email 已被註冊"

    # 驗證通過，回傳新使用者資料
    return True, {
        "username": username, "email": email, "password": password,
        "phone": phone, "birthdate": birthdate
    }

def verify_login(email, password, users):
    """驗證登入：比對 Email + 密碼，回傳 (是否成功, 使用者資料或錯誤訊息)"""
    if not email or not password:
        return False, "請輸入 Email 與密碼"

    for user in users:
        if user["email"] == email and user["password"] == password:
            return True, user
    return False, "Email 或密碼錯誤"

# ===== 自訂過濾器 =====

@app.template_filter('mask_phone')
def mask_phone(phone):
    """電話遮罩：0912345678 → 0912****78"""
    if not phone or len(phone) != 10 or not phone.startswith("09"):
        return phone or "未填寫"
    return phone[:4] + "****" + phone[-2:]

@app.template_filter('format_tw_date')
def format_tw_date(date_str):
    """西元年 → 民國年：2025-05-23 → 民國114年05月23日"""
    try:
        y, m, d = date_str.split("-")
        return f"民國{int(y) - 1911}年{m}月{d}日"
    except:
        return date_str

# ===== 路由 =====

@app.route('/')
def index():
    return render_template('index.html', title='簡易會員系統')

@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        # 簡單收集表單資料
        form = {}
        for field in ["username", "email", "password", "phone", "birthdate"]:
            form[field] = request.form.get(field, "").strip()

        data = load_users()
        ok, result = validate_register(form, data["users"])

        if not ok:
            return redirect(url_for('error_route', message=result))

        data["users"].append(result)
        if not save_users(data):
            return redirect(url_for('error_route', message='寫入失敗'))
        return redirect(url_for('login_route'))

    return render_template('register.html', title='會員註冊')

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        ok, result = verify_login(email, password, load_users()["users"])
        if ok:
            return redirect(url_for('welcome_route', username=result["username"]))
        return redirect(url_for('error_route', message=result))

    return render_template('login.html', title='會員登入')

@app.route('/welcome/<username>')
def welcome_route(username):
    # 簡單迴圈尋找使用者（取代生成器表達式）
    target = None
    for user in load_users()["users"]:
        if user["username"] == username:
            target = user
            break

    if not target:
        return redirect(url_for('error_route', message='查無此使用者'))
    return render_template('welcome.html', title='歡迎登入', user=target)

@app.route('/users')
def users_list_route():
    return render_template('users.html', title='會員清單', users=load_users()["users"])

@app.route('/error')
def error_route():
    message = request.args.get('message', '發生未知錯誤')
    return render_template('error.html', title='系統錯誤', message=message)

# ===== 啟動時自動初始化 JSON 檔案 =====
# 先確認檔案是否存在，不存在才建立預設值（避免每次啟動都重寫）
if not os.path.exists(JSON_FILE):
    save_users(load_users())