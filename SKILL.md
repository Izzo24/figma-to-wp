# Figma to WordPress 分檔工具 v4

## 輸入格式
```
1. 頁面：{page-name}
2. 區塊：{section-name}
3. 備註：{可選}
---
{Figma 代碼}
```

## 兩階段流程

### 第一階段：分析 + 詢問標題

收到代碼後，Claude 執行：
1. 分析 HTML 結構
2. 提取所有可能是標題的文字（排除按鈕）
3. 詢問使用者：

```
我找到這些可能是標題的文字：
1. XXX
2. YYY
3. ZZZ

請告訴我哪個是 H1、H2、H3？
格式：「1是H2，3是H3」（沒有的不用填）
```

### 第二階段：產生檔案

使用者回覆後，Claude 執行：
1. 套用標題層級
2. SEO 語意標籤優化
3. 分離 HTML 與 CSS
4. 輸出檔案

## SEO 優化規則

| 元素 | 優化方式 |
|------|---------|
| 標題 | 依使用者指定的 H1/H2/H3 |
| 按鈕 | → `<a href="#" class="btn">文字</a>` |
| 圖文區 | → `<figure>` + `<figcaption>` |
| 列表項 | → `<ul><li>` |
| 區塊容器 | → `<section>` |
| 空 div | 移除無意義嵌套 |

## 檔案路徑
- PHP → `/pages/page-{page-name}.php`
- CSS → `/assets/css/pages/page-{page-name}.css`

## CSS 規則
- 移除：font-size、line-height、font-family、font-weight、left、top、position、width、height
- class 命名：純英文 BEM 格式
- 合併相同樣式

## Token 優化
- 第一階段只輸出標題列表
- 不重複確認規則
- 完成後只回報檔案路徑
