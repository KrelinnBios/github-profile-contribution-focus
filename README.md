# GitHub Profile Contribution Focus

<p align="center">
  <strong>仓库 × 月份 · 贡献重心 · 自动更新</strong><br>
  为 GitHub 个人主页生成简洁的 12 个月代码贡献时间带
</p>

<p align="center">
  <img src="https://img.shields.io/badge/平台-GitHub%20Actions-247344?style=flat-square" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/许可-MIT-1f5f9c?style=flat-square" alt="MIT License">
</p>

<p align="center">
  <a href="README.md">简体中文</a> ·
  <a href="README.zh-TW.md">繁體中文</a> ·
  <a href="README.en.md">English</a>
</p>

## 项目简介

GitHub Profile Contribution Focus 是一个可复用的 GitHub Action。它读取账号最近 12 个月的公开代码提交贡献，按仓库和月份生成 SVG 时间带，展示这一年主要在做什么，以及项目重心如何变化。

图表只显示贡献量最高的 5 个仓库，其余仓库逐月汇总为 `Other`。生成结果保存在自己的主页仓库中，不依赖外部图片服务。

## 效果预览

<p align="center">
  <img src="examples/preview.svg" alt="过去 12 个月的仓库贡献重心图">
</p>

图表遵循以下固定规则：

- 横向为当前月份及之前 11 个自然月。
- 每行为一个仓库，每个色块代表该仓库当月的提交贡献量。
- 色块分为 4 个相对强度等级，空月份显示为主题色轨道。
- 按 12 个月总提交量排序，显示前 5 个仓库。
- 第 6 个及之后的仓库逐月合并为 `Other`。
- 右侧显示每个仓库在统计周期内的提交总数。
- 同一 SVG 自动适配 GitHub 的浅色与深色模式。

## 使用方式

### 1. 在主页 README 中加入占位图片

```html
<p align="left">
  <img src="./contribution-focus.svg" alt="Contribution focus over the last 12 months" />
</p>
```

第一次运行后，Action 会把占位路径替换为类似 `contribution-focus-a1b2c3d4e5f6.svg` 的版本化文件名，避免 GitHub 图片缓存。

### 2. 添加配置文件

将 [`examples/contribution-focus.config.json`](./examples/contribution-focus.config.json) 复制到主页仓库根目录。

在与用户名同名的个人主页仓库中，最小配置可以是空对象：

```json
{}
```

也可以明确指定账号并覆盖仓库颜色：

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

### 3. 添加更新工作流

将 [`examples/update-contribution-focus.yml`](./examples/update-contribution-focus.yml) 复制到主页仓库的 `.github/workflows/update-contribution-focus.yml`。

核心步骤如下：

```yaml
- name: Generate contribution focus chart
  id: contribution-focus
  uses: KrelinnBios/github-profile-contribution-focus@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    config-path: contribution-focus.config.json
```

示例工作流每天自动更新一次，也支持手动运行。项目发布正式版本后，建议将 `@main` 固定为实际存在的版本标签。

## 统计口径

- 数据来自 GitHub GraphQL API 的 `contributionsCollection`。
- 只统计 GitHub 计入个人贡献记录的 commit contributions，不混入 Issue、Pull Request 或 Review 数量。
- 统计范围为 UTC 下当前月份和之前 11 个自然月；当前月份尚未结束时会以加粗和下划线标记。
- 每个月单独查询，因此单个仓库在一个月内最多只有 31 个贡献日期节点，不会因连接分页丢失月份数据。
- 默认只包含令牌可见的公开贡献；不会在图表中泄露私有仓库名称。
- 排名按整个 12 个月的总提交量计算，`Other` 则按月汇总未进入前 5 名的仓库。

## 配置说明

| 字段 | 默认值 | 说明 |
| --- | --- | --- |
| `owner` | 当前仓库所有者 | 需要统计的 GitHub 用户名 |
| `excluded_repositories` | `[]` | 不参与统计的仓库，可写 `owner/repo` 或仓库名 |
| `colors` | 稳定自动配色 | 用仓库全名、仓库名或 `Other` 覆盖行颜色 |
| `theme` | GitHub 浅色/深色配色 | 覆盖文字和空色块颜色 |

建议使用完整的 `owner/repo` 作为颜色键，避免不同所有者下的同名仓库发生冲突。

可覆盖的主题字段：

- `light_text`、`light_muted`、`light_empty`
- `dark_text`、`dark_muted`、`dark_empty`

## Action 输入与输出

### 输入

| 名称 | 必填 | 默认值 | 用途 |
| --- | --- | --- | --- |
| `github-token` | 是 | 无 | 查询 GitHub 公开贡献数据 |
| `config-path` | 否 | `contribution-focus.config.json` | 配置文件路径 |
| `readme-path` | 否 | `README.md` | 需要更新图片引用的 README |
| `output-directory` | 否 | `.` | SVG 输出目录 |
| `output-prefix` | 否 | `contribution-focus` | 生成文件名前缀 |

### 输出

| 名称 | 说明 |
| --- | --- |
| `image` | 生成的版本化 SVG 路径 |
| `changed` | SVG、README 引用或旧文件是否发生变化 |

## 本地开发

项目只使用 Python 标准库：

```bash
python -m unittest discover -s tests -v
python examples/generate_preview.py
```

## 许可

[MIT](./LICENSE)
