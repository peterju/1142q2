# 第 2 次小考

## 1132 Web 程式設計

:::info
注意事項

- 本小考可參考書籍或網路上任何資料，惟不可以任何方式與第三者交流溝通，若有任何不誠實的投機行為，將依校規辦理，且當次的成績 0 分計算。
- 本次小考請以 Git 上傳 GitHub，再將專案網址貼到【繳交表單連結】，GitHub 專案需完整包含所有檔案。
- 如有專案設定 public 可能遭其他同學看到的疑慮，可設定為 private 再將老師的郵件加入你專案的合作開發，並於群組通知老師收信。
- 繳交時間到之後請勿再更新答案，如超過繳交時間仍更新，則老師會參考繳交時間前最後一次 commit 的答案。
  :::

:::danger
請於 【日期】中午 12:00 以前完成本次作業。
:::

# 簡易會員系統

請使用 Flask 框架設計一個「簡易會員系統」。因課程尚未講授資料庫與 Session，本系統採用 **JSON 檔案** 儲存資料，並模擬無狀態的 Web 請求流程。

## 系統功能需求

1. **首頁（`/`）**：顯示系統標題與簡介，提供「會員清單」、「登入」、「註冊」的連結。
2. **註冊功能（`/register`）**：
   - GET：顯示註冊表單（帳號、Email、密碼、電話、出生日期）。
   - POST：驗證表單資料。若通過驗證，將資料存入 `users.json`，並重定向至登入頁；若失敗，導向錯誤頁。
3. **登入功能（`/login`）**：
   - GET：顯示登入表單（Email、密碼）。
   - POST：驗證 Email 與密碼是否匹配 `users.json` 中的記錄。若匹配，重定向至歡迎頁 `/welcome/<username>`；若失敗，導向錯誤頁。
4. **歡迎頁（`/welcome/<username>`）**：
   - 根據 URL 中的 `username` 從 JSON 查詢該會員資料並顯示。
   - 提供「返回首頁」與「查看會員清單」連結。
5. **會員清單（`/users`）**：
   - GET：讀取 `users.json`，以表格列出所有會員（帳號、Email、電話、出生日期）。
   - **注意**：本清單僅供瀏覽，不提供修改與刪除功能；密碼欄位不得顯示於網頁上。
6. **統一錯誤頁（`/error`）**：
   - 接收 `message` 參數（透過 `request.args`），顯示錯誤訊息。
   - 提供「返回前一頁」與「返回首頁」連結。

## 專案結構

請嚴格依照以下結構建立專案：

```
project/
│
├── app.py
├── requirements.txt
├── templates/
│   ├── base.html          # ← 考題已提供，請勿修改結構
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── welcome.html
│   ├── users.html
│   └── error.html
├── static/
│   └── css/
│       └── style.css
└── users.json             # 程式啟動時若不存在則自動建立
```

## `templates/base.html`

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}會員系統{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header class="container">
        <nav>
            <ul>
                <li><strong>👥 會員系統</strong></li>
            </ul>
            <ul>
                <li><a href="{{ url_for('index') }}">首頁</a></li>
                <li><a href="{{ url_for('users_list_route') }}">會員清單</a></li>
                <li><a href="{{ url_for('login_route') }}">登入</a></li>
                <li><a href="{{ url_for('register_route') }}">註冊</a></li>
            </ul>
        </nav>
    </header>
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    <footer class="container">
        <hr>
        <p><small>1132 Web 程式設計 - 第 2 次小考</small></p>
    </footer>
</body>
</html>
```

:::info 🎨 Pico CSS 使用說明
本作業改用 **Pico CSS v2** 作為前端樣式框架。Pico 強調「語義化 HTML」，**絕大多數元件僅需使用標準標籤即可自動美化**，無需額外撰寫 `class`。

- **按鈕樣式**：預設為主要按鈕。若需次要色調請加 `class="secondary"`，若需外框樣式請加 `class="outline"`。
- **表格響應式**：若表格欄位較多，請在外層包裹 `<div class="overflow-auto">` 以支援手機橫向滑動。
- **避免使用 Bootstrap 語法**：本作業不使用 `.row`, `.col`, `.card`, `.btn-primary` 等類別，請直接依賴 `<article>`, `<form>`, `<button>` 等語義化標籤。
- 為節省排版時間，考題已直接提供 `base.html`，請直接複製使用，勿修改其結構。
:::

:::info 🏷️ HTML5 語意化標籤速查表
為配合 Pico CSS 的設計哲學，本作業使用標準 HTML5 標籤取代大量 `class`。以下為考題中實際會用到的核心標籤：

| 標籤 | 用途 | Pico CSS 對應效果 | 考題使用位置 |
|------|------|-------------------|--------------|
| `<header>` | 頁面或區塊頂部 | 自動調整間距與字體 | `base.html` 導航列外層、`welcome.html` 標題區 |
| `<nav>` | 導航連結區 | 自動轉為橫向排列 | `base.html` 內含 `<ul><li>` 列表 |
| `<main>` | 頁面主要內容 | 設定標準容器寬度 | `base.html`（每頁僅出現一次） |
| `<footer>` | 頁面或區塊底部 | 自動對齊與留白 | `base.html` 頁尾、`index.html` 按鈕區 |
| `<article>` | 獨立內容區塊 | **Pico 核心卡片容器**：自動加圓角、陰影、內距 | 各子模板的 `<div class="container">` 內容區 |
| `<hgroup>` | 標題與副標題組合 | 優化 `h1`~`h6` 與 `p` 的間距 | `index.html` 首頁標題區 |
| `<form>` / `<label>` / `<input>` / `<button>` | 表單與按鈕 | 自動美化輸入框、按鈕 hover 效果 | `register.html`、`login.html` |
| `<table>` / `<thead>` / `<tbody>` / `<tr>` / `<th>` / `<td>` | 資料表格 | 自動加框線、斑马紋、hover 效果 | `users.html`、`welcome.html` |
| `<hr>` | 水平分隔線 | 預設淺灰線與上下間距 | `base.html` 頁尾上方 |
| `<small>` | 輔助說明文字 | 自動縮小字體與降低對比 | `base.html` 版權宣告 |

💡 **實作提示**：
1. **無需額外加 class**：Pico 會自動識別上述標籤並套用樣式，請直接撰寫語意標籤即可。
2. `<article>` 是 Pico 的「萬能容器」：每個功能頁面（表單、結果、錯誤訊息）都建議用 `<article>` 包覆，可獲得完整的卡片視覺效果。
3. **Jinja2 搭配建議**：子模板的 `{% block content %}` 內容，建議直接以 `<article>` 開頭與結尾，確保繼承後版面不會破版。
4. 語意化標籤不僅提升程式可讀性，也有助於無障礙存取 (a11y) 與未來維護。
:::

## JSON 資料結構 (`users.json`)

系統第一次執行時需自動初始化此檔案：

```json
{
  "users": [
    {
      "username": "admin",
      "email": "admin@example.com",
      "password": "admin123",
      "phone": "0912345678",
      "birthdate": "1990-01-01"
    }
  ]
}
```

## 程式設計要求

### 1. 穩定回傳結構與函式封裝

請將核心邏輯封裝為獨立函式，並**統一回傳 dict 結構**：

```python
# 成功範例
{"success": True, "data": {...}}
# 失敗範例
{"success": False, "error": "錯誤訊息"}
```

- 函式不得依賴全域變數，所有資料必須透過參數傳入、`return` 傳出。
- 需實作以下輔助函式：
  - `init_json_file() -> None`：初始化 `users.json`
  - `read_users() -> dict`：讀取 JSON 並回傳 dict
  - `save_users( dict) -> bool`：寫入 JSON
  - `validate_register(form_ dict) -> dict`：驗證註冊資料
  - `verify_login(email: str, password: str, users: list) -> dict`：驗證登入

### 2. 表單驗證規則

- 帳號、Email、密碼、出生日期為必填（不可為空或純空白）。
- Email 必須包含 `@` 與 `.`。
- 電話為選填，若有填寫則需為 10 碼數字且開頭為 `09`。
- 密碼長度需介於 6~16 字元。
- 帳號與 Email 不得與 JSON 中既有資料重複。

### 3. 自訂過濾器

在 `app.py` 中定義以下過濾器，並於樣板中實際使用：

```python
@app.template_filter('mask_phone')
def mask_phone(phone: str) -> str:
    """將電話中間 4 碼替換為星號，例：0912345678 -> 0912****78"""
    ...

@app.template_filter('format_tw_date')
def format_tw_date(date_str: str) -> str:
    """將 YYYY-MM-DD 轉為民國格式，例：2025-05-23 -> 民國114年05月23日"""
    ...
```

### 4. 路由與樣板規範

- 所有頁面需使用 `render_template` 渲染，並正確使用 `url_for` 產生連結。
- 表單提交一律使用 `POST` 方法。
- **路由函式命名建議**：為避免與輔助函式衝突，路由函式建議加上 `_route` 後綴，例如：`register_route`, `login_route`, `users_list_route`, `welcome_route`, `error_route`。
- **初始化時機**：`init_json_file()` 必須寫在模組層級（`if __name__` 之外），確保 `flask run` 匯入模組時自動執行。

### 5. 程式碼規範

- 遵循 PEP 8 格式。
- 每個函式需撰寫簡短 docstring 說明功能與回傳值。
- **使用 Python 3.10+ 內建型別提示**（如 `dict`, `list`, `str`, `bool`, `None`），**無需 `import typing`**。
- 檔案讀寫需使用 `try/except` 精準捕捉 `FileNotFoundError` 或 `json.JSONDecodeError`。

## 提示

- 講義第五章強調：防呆與例外處理應精準，不建議使用裸 `except`。
- 講義第一章強調：參數進，return 出；不要偷拿外面的資料。
- 讀取 JSON 範例：
  ```python
  import json
  try:
      with open("users.json", "r", encoding="utf-8") as f:
          return json.load(f)
  except FileNotFoundError:
      return {"users": []}
  except json.JSONDecodeError:
      return {"users": []}
  ```
- 表單取值建議使用預設值防呆：`request.form.get("email", "").strip()`
- **啟動指令**：請統一使用 `flask --debug run`。Flask CLI 會以模組匯入方式載入 `app.py`，因此初始化邏輯需寫在模組層級。

## 自我測試步驟

1. 首次執行 `flask --debug run`，`users.json` 應自動建立且含 `admin` 預設資料。
2. 註冊時未輸入密碼或輸入 `abc@`（無 `.`）的 Email，應導向錯誤頁提示。
3. 使用重複的帳號或 Email 註冊，應導向錯誤頁提示。
4. 登入時使用正確的 `admin@example.com` 與 `admin123`，應成功導向 `/welcome/admin`。
5. 訪問 `/users`，表格應顯示 `admin` 資料，電話顯示 `0912****78`，出生日期顯示民國年，**密碼欄位不可見**。
6. 錯誤頁面點擊「返回前一頁」應回到上一頁。

## 評分標準

| 項目                   | 比重 | 評分重點                                                                        |
| ---------------------- | ---- | ------------------------------------------------------------------------------- |
| **功能完整性**   | 50%  | 6 個核心路由運作正常；JSON 讀寫與初始資料正確；驗證規則落實                     |
| **程式碼規範**   | 20%  | 穩定回傳結構、無全域依賴、PEP 8、docstring、Python 3.10+ 型別提示、精準例外處理 |
| **樣板與過濾器** | 20%  | 正確使用樣板繼承、`url_for`、`request.form/args`、自訂過濾器實際渲染        |
| **頁面體驗**     | 10%  | Pico 語義化標籤應用、必要 class 使用正確、表單清晰、響應式基礎                  |
