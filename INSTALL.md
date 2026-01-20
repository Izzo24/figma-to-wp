# 安裝指南

## Mac 安裝

### 方法 1：終端機指令（推薦）

```bash
# 1. 建立資料夾
mkdir -p ~/.claude/agents/figma-to-wp

# 2. 下載檔案後，複製到目標位置
cp ~/Downloads/SKILL.md ~/.claude/agents/figma-to-wp/
cp ~/Downloads/parser.py ~/.claude/agents/figma-to-wp/
cp ~/Downloads/config.json ~/.claude/agents/figma-to-wp/
cp ~/Downloads/README.md ~/.claude/agents/figma-to-wp/

# 3. 設定執行權限
chmod +x ~/.claude/agents/figma-to-wp/parser.py

# 4. 確認安裝
ls -la ~/.claude/agents/figma-to-wp/
```

### 方法 2：Finder 手動

1. 下載所有檔案
2. 打開 Finder
3. 按 `Cmd + Shift + G`
4. 輸入 `~/.claude/agents/`
5. 建立 `figma-to-wp` 資料夾
6. 把 4 個檔案拖進去

> 💡 看不到 `.claude` 資料夾？按 `Cmd + Shift + .` 顯示隱藏檔案

---

## Windows 安裝

### 方法 1：PowerShell 指令（推薦）

```powershell
# 1. 建立資料夾
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\agents\figma-to-wp"

# 2. 下載檔案後，複製到目標位置
Copy-Item "$env:USERPROFILE\Downloads\SKILL.md" "$env:USERPROFILE\.claude\agents\figma-to-wp\"
Copy-Item "$env:USERPROFILE\Downloads\parser.py" "$env:USERPROFILE\.claude\agents\figma-to-wp\"
Copy-Item "$env:USERPROFILE\Downloads\config.json" "$env:USERPROFILE\.claude\agents\figma-to-wp\"
Copy-Item "$env:USERPROFILE\Downloads\README.md" "$env:USERPROFILE\.claude\agents\figma-to-wp\"

# 3. 確認安裝
Get-ChildItem "$env:USERPROFILE\.claude\agents\figma-to-wp"
```

### 方法 2：CMD 指令

```cmd
:: 1. 建立資料夾
mkdir %USERPROFILE%\.claude\agents\figma-to-wp

:: 2. 複製檔案
copy %USERPROFILE%\Downloads\SKILL.md %USERPROFILE%\.claude\agents\figma-to-wp\
copy %USERPROFILE%\Downloads\parser.py %USERPROFILE%\.claude\agents\figma-to-wp\
copy %USERPROFILE%\Downloads\config.json %USERPROFILE%\.claude\agents\figma-to-wp\
copy %USERPROFILE%\Downloads\README.md %USERPROFILE%\.claude\agents\figma-to-wp\

:: 3. 確認安裝
dir %USERPROFILE%\.claude\agents\figma-to-wp
```

### 方法 3：檔案總管手動

1. 下載所有檔案
2. 打開檔案總管
3. 在網址列輸入 `%USERPROFILE%\.claude\agents\`
4. 建立 `figma-to-wp` 資料夾
5. 把 4 個檔案拖進去

> 💡 看不到 `.claude` 資料夾？在檔案總管「檢視」→ 勾選「隱藏的項目」

---

## 安裝路徑對照

| 系統 | 路徑 |
|------|------|
| Mac | `~/.claude/agents/figma-to-wp/` |
| Windows | `C:\Users\你的名字\.claude\agents\figma-to-wp\` |

---

## 確認安裝成功

安裝完成後，資料夾內應有 4 個檔案：

```
figma-to-wp/
├── SKILL.md
├── parser.py
├── config.json
└── README.md
```

---

## 需要 Python

確保電腦有安裝 Python 3：

```bash
# Mac / Windows
python3 --version
```

如果沒有，請到 [python.org](https://www.python.org/downloads/) 下載安裝。
