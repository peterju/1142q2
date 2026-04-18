"""
簡易會員系統 (JSON 檔案儲存版)
1132 Web 程式設計 - 第 2 次小考解答
"""
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
JSON_FILE = "users.json"

# ===== JSON 檔案輔助函式 =====

def default_users_data() -> dict:
    """回傳系統初始化用的預設會員資料。"""
    return {
        "users": [{
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "phone": "0912345678",
            "birthdate": "1990-01-01"
        }]
    }

def init_json_file(file_path: str) -> None:
    """初始化 users.json，若不存在或為空則建立含預設 admin 的結構"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read().strip()
            if not raw_content:  # 檔案存在但為空
                raise ValueError("Empty file")
            json.loads(raw_content)
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        save_users(file_path, default_users_data())

def read_users(file_path: str) -> dict:
    """讀取 JSON 並回傳 dict；若檔案不存在或格式錯誤則回傳預設結構"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_users_data()

def save_users(file_path: str, data: dict) -> bool:
    """將 dict 寫入 JSON 檔案，成功回傳 True，失敗回傳 False"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            # indent=2 提升可讀性，ensure_ascii=False 支援中文
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (OSError, TypeError, ValueError):
        return False

# ===== 業務邏輯與驗證函式 =====

def validate_register(form_data: dict, users: list) -> dict:
    """
    驗證註冊表單資料，檢查格式、長度與重複性。
    驗證通過則回傳可寫入的新使用者資料。
    """
    username = form_data.get("username", "").strip()
    email = form_data.get("email", "").strip()
    password = form_data.get("password", "").strip()
    phone = form_data.get("phone", "").strip()
    birthdate = form_data.get("birthdate", "").strip()

    # 1. 必填欄位檢查
    if not username or not email or not password or not birthdate:
        return {"success": False, "error": "帳號、Email、密碼與出生日期為必填欄位"}

    # 2. Email 格式簡易檢查
    if "@" not in email or "." not in email.split("@")[-1]:
        return {"success": False, "error": "Email 格式錯誤"}

    # 3. 密碼長度限制
    if not (6 <= len(password) <= 16):
        return {"success": False, "error": "密碼長度需為 6~16 字元"}

    # 4. 電話選填驗證
    if phone and (not phone.isdigit() or len(phone) != 10 or not phone.startswith("09")):
        return {"success": False, "error": "電話需為 10 碼數字且以 09 開頭"}

    # 5. 重複檢查
    for u in users:
        if u.get("username") == username:
            return {"success": False, "error": "該帳號已被註冊"}
        if u.get("email") == email:
            return {"success": False, "error": "該 Email 已被註冊"}

    # 6. 建立新資料
    new_user = {
        "username": username, "email": email, "password": password,
        "phone": phone, "birthdate": birthdate
    }
    return {"success": True, "data": new_user}

def verify_login(email: str, password: str, users: list) -> dict:
    """
    比對 Email 與密碼是否匹配。
    成功回傳使用者 dict，失敗回傳錯誤訊息。
    """
    if not email or not password:
        return {"success": False, "error": "請輸入 Email 與密碼"}

    for user in users:
        if user.get("email") == email and user.get("password") == password:
            return {"success": True, "data": user}

    return {"success": False, "error": "Email 或密碼錯誤"}

# ===== 自訂過濾器 =====

@app.template_filter('mask_phone')
def mask_phone(phone: str) -> str:
    """電話遮罩：0912345678 -> 0912****78"""
    if not phone:
        return "未填寫"
    if len(phone) == 10 and phone.startswith("09"):
        return phone[:4] + "****" + phone[-2:]
    return phone

@app.template_filter('format_tw_date')
def format_tw_date(date_str: str) -> str:
    """西元年轉民國年：2025-05-23 -> 民國114年05月23日"""
    try:
        y, m, d = date_str.split("-")
        return f"民國{int(y) - 1911}年{m}月{d}日"
    except ValueError:
        return date_str  # 格式不符時原樣回傳

# ===== Flask 路由 =====

@app.route('/')
def index() -> str:
    """首頁：顯示系統標題與導航連結"""
    return render_template('index.html', title='簡易會員系統')

@app.route('/register', methods=['GET', 'POST'])
def register_route() -> str:
    """註冊頁：GET 顯示表單，POST 驗證並寫檔"""
    if request.method == 'POST':
        # 收集表單資料並去除首尾空白
        form_data = {k: request.form.get(k, "") for k in ["username", "email", "password", "phone", "birthdate"]}
        data = read_users(JSON_FILE)
        result = validate_register(form_data, data.get("users", []))
        if not result["success"]:
            return redirect(url_for('error_route', message=result["error"]))

        # 驗證函式只負責檢查資料，實際寫回 JSON 留在路由中處理。
        data.setdefault("users", []).append(result["data"])
        if not save_users(JSON_FILE, data):
            return redirect(url_for('error_route', message='會員資料寫入失敗，請稍後再試'))
        return redirect(url_for('login_route'))
    return render_template('register.html', title='會員註冊')

@app.route('/login', methods=['GET', 'POST'])
def login_route() -> str:
    """登入頁：GET 顯示表單，POST 驗證並導向歡迎頁"""
    if request.method == 'POST':
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        result = verify_login(email, password, read_users(JSON_FILE).get("users", []))
        if result["success"]:
            return redirect(url_for('welcome_route', username=result["data"]["username"]))
        return redirect(url_for('error_route', message=result["error"]))
    return render_template('login.html', title='會員登入')

@app.route('/welcome/<username>')
def welcome_route(username: str) -> str:
    """歡迎頁：根據 username 查詢並顯示單一會員資料"""
    # 使用生成器表達式快速比對
    target = next((u for u in read_users(JSON_FILE).get("users", []) if u.get("username") == username), None)
    if target is None:
        return redirect(url_for('error_route', message='查無此使用者'))
    return render_template('welcome.html', title='歡迎登入', user=target)

@app.route('/users')
def users_list_route() -> str:
    """會員清單頁：讀取 JSON 並渲染表格"""
    return render_template('users.html', title='會員清單', users=read_users(JSON_FILE).get("users", []))

@app.route('/error')
def error_route() -> str:
    """錯誤頁：接收 query string 的 message 參數並顯示"""
    message = request.args.get('message', '發生未知錯誤')
    return render_template('error.html', title='系統錯誤', message=message)

# ===== 程式啟動初始化（模組匯入時立即執行） =====
# 此處不在 if __name__ == '__main__' 內，確保 flask run 也能執行
init_json_file(JSON_FILE)
