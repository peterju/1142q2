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

def init_json_file(file_path: str) -> None:
    """若 JSON 檔案不存在，則建立預設資料"""
    if not os.path.exists(file_path):
        save_users(file_path, _default_data())

def _default_data() -> dict:
    """內部輔助：預設 admin 資料"""
    return {
        "users": [{
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "phone": "0912345678",
            "birthdate": "1990-01-01"
        }]
    }

def read_users(file_path: str) -> dict:
    """讀取 JSON，錯誤時回傳預設資料"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return _default_data()

def save_users(file_path: str, data: dict) -> bool:
    """寫入 JSON，成功回傳 True，失敗回傳 False"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ===== 驗證邏輯（✅ 參數名稱修正為 form_data） =====

def validate_register(form_data: dict, users: list) -> dict:
    """
    驗證註冊資料
    ✅ 參數是 form_data（不是 form_！）
    """
    # ✅ 用 form_data 取值
    username = form_data.get("username", "").strip()
    email = form_data.get("email", "").strip()
    password = form_data.get("password", "").strip()
    phone = form_data.get("phone", "").strip()
    birthdate = form_data.get("birthdate", "").strip()

    # 必填檢查
    if not username or not email or not password or not birthdate:
        return {"success": False, "error": "帳號、Email、密碼與出生日期為必填欄位"}

    # Email 簡易檢查
    if "@" not in email or "." not in email.split("@")[-1]:
        return {"success": False, "error": "Email 格式錯誤"}

    # 密碼長度
    if not (6 <= len(password) <= 16):
        return {"success": False, "error": "密碼長度需為 6~16 字元"}

    # 電話格式（選填）
    if phone and (not phone.isdigit() or len(phone) != 10 or not phone.startswith("09")):
        return {"success": False, "error": "電話需為 10 碼數字且以 09 開頭"}

    # 重複檢查
    for u in users:
        if u["username"] == username:
            return {"success": False, "error": "該帳號已被註冊"}
        if u["email"] == email:
            return {"success": False, "error": "該 Email 已被註冊"}

    # 驗證通過
    return {"success": True, "data": {
        "username": username, "email": email, "password": password,
        "phone": phone, "birthdate": birthdate
    }}

def verify_login(email: str, password: str, users: list) -> dict:
    """驗證登入"""
    if not email or not password:
        return {"success": False, "error": "請輸入 Email 與密碼"}

    for user in users:
        if user["email"] == email and user["password"] == password:
            return {"success": True, "data": user}

    return {"success": False, "error": "Email 或密碼錯誤"}

# ===== 自訂過濾器 =====

@app.template_filter('mask_phone')
def mask_phone(phone: str) -> str:
    """電話遮罩"""
    if not phone or len(phone) != 10 or not phone.startswith("09"):
        return phone or "未填寫"
    return phone[:4] + "****" + phone[-2:]

@app.template_filter('format_tw_date')
def format_tw_date(date_str: str) -> str:
    """西元年 → 民國年"""
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
    """註冊頁"""
    if request.method == 'POST':
        # 收集表單（用有意義的變數名稱 form_data）
        form_data = {}
        for field in ["username", "email", "password", "phone", "birthdate"]:
            form_data[field] = request.form.get(field, "").strip()

        data = read_users(JSON_FILE)
        # ✅ 傳 form_data 給驗證函式
        result = validate_register(form_data, data["users"])

        if not result["success"]:
            return redirect(url_for('error_route', message=result["error"]))

        data["users"].append(result["data"])
        if not save_users(JSON_FILE, data):
            return redirect(url_for('error_route', message='寫入失敗'))
        return redirect(url_for('login_route'))

    return render_template('register.html', title='會員註冊')

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    """登入頁"""
    if request.method == 'POST':
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        result = verify_login(email, password, read_users(JSON_FILE)["users"])
        if result["success"]:
            return redirect(url_for('welcome_route', username=result["data"]["username"]))
        return redirect(url_for('error_route', message=result["error"]))

    return render_template('login.html', title='會員登入')

@app.route('/welcome/<username>')
def welcome_route(username: str):
    """歡迎頁：用簡單 for 迴圈找使用者"""
    users = read_users(JSON_FILE)["users"]
    target = None
    for user in users:
        if user["username"] == username:
            target = user
            break

    if not target:
        return redirect(url_for('error_route', message='查無此使用者'))
    return render_template('welcome.html', title='歡迎登入', user=target)

@app.route('/users')
def users_list_route():
    """會員清單"""
    return render_template('users.html', title='會員清單', users=read_users(JSON_FILE)["users"])

@app.route('/error')
def error_route():
    """錯誤頁"""
    message = request.args.get('message', '發生未知錯誤')
    return render_template('error.html', title='系統錯誤', message=message)

# ===== 模組層級初始化 =====
init_json_file(JSON_FILE)