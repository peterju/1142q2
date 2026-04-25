"""
簡易會員系統 (JSON 檔案儲存版)
1132 Web 程式設計 - 第 2 次小考解答
"""
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
JSON_FILE = "users.json"  # 定義 JSON 檔案路徑為常數，方便後續維護

# ===== JSON 檔案輔助函式 =====

def default_users_data() -> dict:
    """
    回傳系統初始化用的預設會員資料。
    用途：當 users.json 不存在或損毀時，提供一個預設的 admin 帳號。
    """
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
    """
    初始化 users.json 檔案。
    邏輯：
    1. 嘗試讀取檔案
    2. 如果檔案不存在、為空、或內容不是合法 JSON → 建立預設資料
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read().strip()
            if not raw_content:  # 檔案存在但為空字串
                raise ValueError("Empty file")
            json.loads(raw_content)  # 檢查是否為合法 JSON
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        # 任何錯誤發生時，就寫入預設資料
        save_users(file_path, default_users_data())

def read_users(file_path: str) -> dict:
    """
    讀取 JSON 檔案並回傳 dict。
    如果讀取失敗（檔案不存在或格式錯誤），回傳預設結構避免程式崩潰。
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_users_data()

def save_users(file_path: str, data: dict) -> bool:
    """
    將 dict 資料寫入 JSON 檔案。
    參數：
        file_path: 檔案路徑
        data: 要寫入的字典資料
    回傳：成功回傳 True，失敗回傳 False
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            # indent=2：讓 JSON 縮排好看，方便除錯
            # ensure_ascii=False：讓中文能正常顯示，不會變成 \uXXXX
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (OSError, TypeError, ValueError):
        # 寫入失敗可能原因：權限不足、磁碟滿、資料無法序列化...
        return False

# ===== 業務邏輯與驗證函式 =====

def validate_register(form_data: dict, users: list) -> dict:
    """
    驗證註冊表單資料。
    檢查項目：必填欄位、Email 格式、密碼長度、電話格式、帳號/Email 是否重複。

    回傳格式：
        成功：{"success": True, "data": 新使用者字典}
        失敗：{"success": False, "error": "錯誤訊息"}
    """
    # 【教學重點】逐一取出表單資料並去除首尾空白
    # 原進階寫法（字典推導式，初學者較難理解）：
    # form_data = {k: request.form.get(k, "").strip() for k in ["username", "email", "password", "phone", "birthdate"]}

    # ✅ 簡單版：用傳統方式逐一取值，邏輯清晰易懂
    username = form_data.get("username", "").strip()
    email = form_data.get("email", "").strip()
    password = form_data.get("password", "").strip()
    phone = form_data.get("phone", "").strip()
    birthdate = form_data.get("birthdate", "").strip()

    # 1️⃣ 檢查必填欄位：只要有任一欄位為空，就回傳錯誤
    if not username or not email or not password or not birthdate:
        return {"success": False, "error": "帳號、Email、密碼與出生日期為必填欄位"}

    # 2️⃣ 檢查 Email 格式（簡易版）：必須包含 @ 且 @ 後面要有 .
    # 注意：這不是嚴格的 Email 驗證，僅符合本作業需求
    if "@" not in email or "." not in email.split("@")[-1]:
        return {"success": False, "error": "Email 格式錯誤"}

    # 3️⃣ 檢查密碼長度：必須在 6~16 個字元之間
    if not (6 <= len(password) <= 16):
        return {"success": False, "error": "密碼長度需為 6~16 字元"}

    # 4️⃣ 電話欄位為「選填」，但有填寫時才需要驗證格式
    if phone:  # 如果 phone 不是空字串
        # 檢查：必須全是數字、長度為 10、且以 09 開頭
        if not phone.isdigit() or len(phone) != 10 or not phone.startswith("09"):
            return {"success": False, "error": "電話需為 10 碼數字且以 09 開頭"}

    # 5️⃣ 檢查帳號與 Email 是否已存在（遍歷現有使用者清單）
    for u in users:
        if u.get("username") == username:
            return {"success": False, "error": "該帳號已被註冊"}
        if u.get("email") == email:
            return {"success": False, "error": "該 Email 已被註冊"}

    # ✅ 所有驗證通過，準備回傳新使用者資料
    new_user = {
        "username": username,
        "email": email,
        "password": password,
        "phone": phone,
        "birthdate": birthdate
    }
    return {"success": True, "data": new_user}

def verify_login(email: str, password: str, users: list) -> dict:
    """
    驗證登入：比對 Email 與密碼是否匹配。

    回傳格式：
        成功：{"success": True, "data": 使用者字典}
        失敗：{"success": False, "error": "錯誤訊息"}
    """
    # 先檢查是否有輸入
    if not email or not password:
        return {"success": False, "error": "請輸入 Email 與密碼"}

    # 逐一比對使用者清單
    for user in users:
        # 如果找到 Email 和密碼都符合的使用者
        if user.get("email") == email and user.get("password") == password:
            return {"success": True, "data": user}

    # 跑完迴圈都沒找到 → 登入失敗
    return {"success": False, "error": "Email 或密碼錯誤"}

# ===== 自訂過濾器（用於 Jinja2 模板） =====

@app.template_filter('mask_phone')
def mask_phone(phone: str) -> str:
    """
    電話遮罩過濾器：將手機號碼中間 4 碼替換為 ****
    範例：0912345678 → 0912****78
    """
    # 如果電話為空，顯示預設文字
    if not phone:
        return "未填寫"

    # 如果是標準 10 碼且以 09 開頭，才進行遮罩
    if len(phone) == 10 and phone.startswith("09"):
        # 取前 4 碼 + **** + 後 2 碼
        return phone[:4] + "****" + phone[-2:]

    # 格式不符，原樣回傳
    return phone

@app.template_filter('format_tw_date')
def format_tw_date(date_str: str) -> str:
    """
    日期格式轉換過濾器：西元年 → 民國年
    範例：2025-05-23 → 民國114年05月23日
    """
    try:
        # 先用 split 把日期字串拆成年、月、日
        y, m, d = date_str.split("-")
        # 民國年 = 西元年 - 1911
        tw_year = int(y) - 1911
        return f"民國{tw_year}年{m}月{d}日"
    except ValueError:
        # 如果日期格式不符（例如無法 split 或轉換 int），原樣回傳
        return date_str

# ===== Flask 路由 =====

@app.route('/')
def index() -> str:
    """首頁：顯示系統標題與導航連結"""
    return render_template('index.html', title='簡易會員系統')

@app.route('/register', methods=['GET', 'POST'])
def register_route() -> str:
    """
    註冊頁面路由：
    - GET：顯示註冊表單
    - POST：接收表單、驗證、寫入 JSON、導向登入頁
    """
    if request.method == 'POST':
        # 【教學重點】收集表單資料並去除首尾空白

        # ❌ 原進階寫法（字典推導式，初學者可能看不懂）：
        # form_data = {k: request.form.get(k, "").strip() for k in ["username", "email", "password", "phone", "birthdate"]}

        # ✅ 簡單版：用傳統迴圈逐一取值，每一步都看得懂
        form_data = {}
        fields = ["username", "email", "password", "phone", "birthdate"]
        for field in fields:
            # 從 request.form 取值，如果沒有該欄位則給空字串，再去除首尾空白
            value = request.form.get(field, "").strip()
            form_data[field] = value

        # 讀取現有使用者資料
        data = read_users(JSON_FILE)
        users_list = data.get("users", [])  # 取出 users 清單，避免 KeyError

        # 呼叫驗證函式
        result = validate_register(form_data, users_list)

        # 如果驗證失敗，導向錯誤頁面
        if not result["success"]:
            return redirect(url_for('error_route', message=result["error"]))

        # ✅ 驗證通過，將新使用者加入清單
        # 使用 setdefault 確保 "users" 鍵存在（防禦性寫法）
        data.setdefault("users", []).append(result["data"])

        # 嘗試寫入 JSON 檔案
        if not save_users(JSON_FILE, data):
            return redirect(url_for('error_route', message='會員資料寫入失敗，請稍後再試'))

        # 註冊成功，導向登入頁面
        return redirect(url_for('login_route'))

    # GET 請求：顯示註冊表單
    return render_template('register.html', title='會員註冊')

@app.route('/login', methods=['GET', 'POST'])
def login_route() -> str:
    """
    登入頁面路由：
    - GET：顯示登入表單
    - POST：驗證帳號密碼，成功則導向歡迎頁
    """
    if request.method == 'POST':
        # 取得並清理使用者輸入
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        # 讀取使用者清單並驗證
        data = read_users(JSON_FILE)
        users_list = data.get("users", [])
        result = verify_login(email, password, users_list)

        if result["success"]:
            # 登入成功：導向歡迎頁，並帶入 username
            return redirect(url_for('welcome_route', username=result["data"]["username"]))
        else:
            # 登入失敗：導向錯誤頁並顯示訊息
            return redirect(url_for('error_route', message=result["error"]))

    # GET 請求：顯示登入表單
    return render_template('login.html', title='會員登入')

@app.route('/welcome/<username>')
def welcome_route(username: str) -> str:
    """
    歡迎頁面：根據 URL 中的 username 查詢並顯示該會員資料。
    如果找不到該使用者，導向錯誤頁。
    """
    # 讀取所有使用者
    data = read_users(JSON_FILE)
    users_list = data.get("users", [])

    # 【教學重點】在清單中尋找符合 username 的使用者

    # ❌ 原進階寫法（生成器表達式 + next()，初學者較難理解）：
    # target = next((u for u in users_list if u.get("username") == username), None)

    # ✅ 簡單版：用傳統 for 迴圈逐一比對
    target = None  # 先假設找不到
    for user in users_list:
        if user.get("username") == username:  # 如果找到符合的使用者
            target = user  # 記錄下來
            break  # 找到就可以離開迴圈，不用繼續找

    # 如果 target 還是 None，代表查無此人
    if target is None:
        return redirect(url_for('error_route', message='查無此使用者'))

    # 找到使用者，渲染歡迎頁面
    return render_template('welcome.html', title='歡迎登入', user=target)

@app.route('/users')
def users_list_route() -> str:
    """會員清單頁：讀取 JSON 並渲染表格（不顯示密碼）"""
    data = read_users(JSON_FILE)
    users_list = data.get("users", [])
    return render_template('users.html', title='會員清單', users=users_list)

@app.route('/error')
def error_route() -> str:
    """
    錯誤頁面：接收 query string 的 message 參數並顯示。
    範例：/error?message=帳號已存在
    """
    # 從 URL 參數取得錯誤訊息，如果沒有則給預設文字
    message = request.args.get('message', '發生未知錯誤')
    return render_template('error.html', title='系統錯誤', message=message)

# ===== 程式啟動初始化 =====
# 【重要】這行寫在模組層級（不在 if __name__ == '__main__' 內）
# 目的是：無論用 `flask run` 或 `python app.py` 啟動，都會自動初始化 JSON 檔案
init_json_file(JSON_FILE)