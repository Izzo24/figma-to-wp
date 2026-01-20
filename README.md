# Figma to WordPress 分檔工具

將 Figma 輸出的 HTML 代碼自動分離為 PHP 與 CSS，並進行 SEO 優化。

## 功能

- ✅ HTML / CSS 自動分離
- ✅ SEO 語意標籤優化（H1/H2/H3）
- ✅ 按鈕自動轉為 `<a href="#">`
- ✅ 純英文 BEM class 命名
- ✅ 合併相同 CSS 規則
- ✅ 移除不必要的 CSS（font-size、position 等）
- ✅ 多區塊追加模式

## 安裝

```bash
# 複製到 Claude agents 目錄
mkdir -p ~/.claude/agents/figma-to-wp
cp SKILL.md parser.py config.json ~/.claude/agents/figma-to-wp/
```

## 使用方式

### 在 Claude Code 中

```
1. 頁面：about
2. 區塊：hero
3. 備註：首頁主視覺
---
<div data-layer="Frame 1" style="...">
  ...Figma 代碼...
</div>
```

### 流程

1. 貼上代碼
2. Claude 分析並列出可能的標題
3. 你指定哪個是 H1/H2/H3（格式：`1是H2，3是H3`）
4. Claude 產生檔案

### 輸出

```
/pages/page-about.php
/assets/css/pages/page-about.css
```

## 檔案結構

```
figma-to-wp/
├── SKILL.md      # Claude 指令說明
├── parser.py     # 主要解析程式
├── config.json   # 設定檔
└── README.md     # 本文件
```

## 設定

編輯 `config.json`：

```json
{
  "php_path": "pages/page-{name}.php",
  "css_path": "assets/css/pages/page-{name}.css",
  "css_remove": [
    "font-size",
    "line-height",
    "font-family",
    "font-weight",
    "left",
    "top",
    "position",
    "width",
    "height"
  ]
}
```

## 輸出範例

### PHP

```html
<!-- ========== 區塊：hero ========== -->
<section class="hero">
    <div class="hero__wrap">
        <h2 class="hero__title">
            標題文字
        </h2>
        <div class="hero__content">
            內容文字
        </div>
        <a href="#" class="hero__btn">按鈕文字</a>
    </div>
</section>
```

### CSS

```css
/* ========== 區塊：hero ========== */

.hero__wrap {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.hero__title {
    color: #0B2341;
    text-align: center;
}

.hero__btn {
    background: linear-gradient(90deg, #FF942B 0%, #FFDC37 100%);
    border-radius: 30px;
}
```

## 命令列使用（可選）

```bash
# 分析模式（只列出標題）
python parser.py --analyze --input figma.html

# 產生檔案
python parser.py \
  --page about \
  --section hero \
  --input figma.html \
  --headings '{"標題文字":"h2"}' \
  --base /path/to/project
```

## 授權

MIT License
