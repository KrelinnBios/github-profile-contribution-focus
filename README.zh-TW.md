# GitHub Profile Contribution Focus

<p align="center">
  <strong>儲存庫 × 月份 · 貢獻重心 · 自動更新</strong><br>
  為 GitHub 個人主頁產生簡潔的 12 個月程式碼貢獻時間帶
</p>

<p align="center">
  <img src="https://img.shields.io/badge/平台-GitHub%20Actions-247344?style=flat-square" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/授權-MIT-1f5f9c?style=flat-square" alt="MIT License">
</p>

<p align="center">
  <a href="README.md">简体中文</a> ·
  <a href="README.zh-TW.md">繁體中文</a> ·
  <a href="README.en.md">English</a>
</p>

## 專案簡介

GitHub Profile Contribution Focus 是一個可重複使用的 GitHub Action。它讀取帳號最近 12 個月的公開程式碼提交貢獻，依儲存庫和月份產生 SVG 時間帶，呈現這一年主要在做什麼，以及專案重心如何變化。

圖表只顯示貢獻量最高的 5 個儲存庫，其餘儲存庫逐月彙總為 `Other`。產生結果保存在自己的個人主頁儲存庫中，不依賴外部圖片服務。

## 功能概覽

- 十二月時間帶：橫向顯示目前月份及之前 11 個自然月。
- 儲存庫貢獻列：每列對應一個儲存庫，每個色塊表示該儲存庫當月的提交貢獻量。
- 相對強度：使用 4 個強度等級區分活躍程度，空月份顯示為主題色軌道。
- 貢獻重心：依 12 個月總提交量顯示前 5 個儲存庫，其餘儲存庫逐月彙總為 `Other`。
- 提交總數：右側顯示每個儲存庫在統計期間內的提交總數。
- 主題適配：同一份 SVG 自動響應 GitHub 的淺色與深色模式。
- 快取處理：使用內容摘要產生版本化檔名，並自動清理舊圖。

## 效果預覽

<p align="center">
  <img src="examples/preview.svg" alt="過去 12 個月的儲存庫貢獻重心圖">
</p>

## 使用方式

### 1. 在個人主頁 README 中加入佔位圖片

```html
<p align="left">
  <img src="./contribution-focus.svg" alt="Contribution focus over the last 12 months" />
</p>
```

第一次執行後，Action 會把佔位路徑替換為類似 `contribution-focus-a1b2c3d4e5f6.svg` 的版本化檔名，避免 GitHub 圖片快取。

### 2. 新增設定檔

將 [`examples/contribution-focus.config.json`](./examples/contribution-focus.config.json) 複製到個人主頁儲存庫根目錄。

在與使用者名稱同名的公開個人主頁儲存庫中，最小設定可以是空物件：

```json
{}
```

也可以明確指定帳號並覆寫儲存庫顏色：

```json
{
  "owner": "YOUR_GITHUB_USERNAME",
  "excluded_repositories": [],
  "colors": {
    "YOUR_GITHUB_USERNAME/your-repository": "#7F52FF",
    "Other": "#8B949E"
  }
}
```

### 3. 新增更新工作流程

將 [`examples/update-contribution-focus.yml`](./examples/update-contribution-focus.yml) 複製到個人主頁儲存庫的 `.github/workflows/update-contribution-focus.yml`。

核心步驟如下：

```yaml
- name: Generate contribution focus chart
  id: contribution-focus
  uses: KrelinnBios/github-profile-contribution-focus@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    config-path: contribution-focus.config.json
```

範例工作流程每天自動更新一次，也支援手動執行。專案發布正式版本後，建議將 `@main` 固定為實際存在的版本標籤。

## 統計口徑

- 資料來自 GitHub GraphQL API 的 `contributionsCollection`。
- 只統計 GitHub 計入個人貢獻記錄的 commit contributions，不混入 Issue、Pull Request 或 Review 數量。
- 統計範圍為 UTC 下目前月份和之前 11 個自然月；尚未結束的目前月份會以粗體和底線標示。
- 每個月份單獨查詢，因此單一儲存庫在一個月內最多只有 31 個貢獻日期節點，不會因連線分頁遺失月份資料。
- 預設只包含權杖可見的公開貢獻；不會在圖表中洩露私有儲存庫名稱。
- 排名依整個 12 個月的總提交量計算，`Other` 則逐月彙總未進入前 5 名的儲存庫。

## 設定說明

| 欄位 | 預設值 | 說明 |
| --- | --- | --- |
| `owner` | 目前儲存庫擁有者 | 需要統計的 GitHub 使用者名稱 |
| `excluded_repositories` | `[]` | 不參與統計的儲存庫，可寫 `owner/repo` 或儲存庫名稱 |
| `colors` | 穩定自動配色 | 以儲存庫全名、儲存庫名稱或 `Other` 覆寫列顏色 |
| `theme` | GitHub 淺色/深色配色 | 覆寫文字和空色塊顏色 |

建議使用完整的 `owner/repo` 作為顏色鍵，避免不同擁有者下的同名儲存庫發生衝突。

可覆寫的主題欄位：`light_text`、`light_muted`、`light_empty`、`dark_text`、`dark_muted`、`dark_empty`。

## Action 輸入與輸出

### 輸入

| 名稱 | 必填 | 預設值 | 用途 |
| --- | --- | --- | --- |
| `github-token` | 是 | 無 | 查詢 GitHub 公開貢獻資料 |
| `config-path` | 否 | `contribution-focus.config.json` | 設定檔路徑 |
| `readme-path` | 否 | `README.md` | 需要更新圖片引用的 README |
| `output-directory` | 否 | `.` | SVG 輸出目錄 |
| `output-prefix` | 否 | `contribution-focus` | 產生檔名前綴 |

### 輸出

| 名稱 | 說明 |
| --- | --- |
| `image` | 產生的版本化 SVG 路徑 |
| `changed` | SVG、README 引用或舊檔案是否發生變化 |

## 本機開發

專案只使用 Python 標準函式庫：

```bash
python -m unittest discover -s tests -v
python examples/generate_preview.py
```

## 授權協議

本專案依據 [MIT License](./LICENSE) 發布，允許使用、修改、散布與商業使用，但須保留授權條款與版權聲明。

## 回饋與貢獻

歡迎透過 [GitHub Issue](https://github.com/KrelinnBios/github-profile-contribution-focus/issues) 提交使用問題、統計口徑疑問、功能建議或其他改進建議。
