# GitHub Profile Contribution Focus

<p align="center">
  <strong>仓库 × 月份 · 贡献重心 · 自动更新</strong><br>
  基于 GitHub「Last year」统计范围生成简洁的贡献重心图
</p>

<p align="center">
  <a href="https://github.com/KrelinnBios/github-profile-contribution-focus/releases"><img src="https://img.shields.io/github/v/release/KrelinnBios/github-profile-contribution-focus?style=flat-square&label=%E7%89%88%E6%9C%AC&color=7F52FF" alt="最新版本"></a>
  <img src="https://img.shields.io/badge/平台-GitHub%20Actions-247344?style=flat-square" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/许可-MIT-1f5f9c?style=flat-square" alt="MIT License">
</p>

<p align="center">
  <a href="README.md">简体中文</a> ·
  <a href="README.zh-TW.md">繁體中文</a> ·
  <a href="README.en.md">English</a>
</p>

## 项目简介

GitHub Profile Contribution Focus 是一个可复用的 GitHub Action。它读取 GitHub 个人主页「Last year」范围内的可见贡献，按仓库和月份生成 SVG 时间带，展示这一年主要参与了哪些项目，以及贡献重心如何变化。

图表只显示贡献量最高的 5 个仓库，其余仓库和无法安全归属到具体仓库的贡献逐月汇总为 `Other`。生成结果保存在自己的主页仓库中，不依赖外部图片服务。

## 功能概览

- GitHub「Last year」时间带：直接采用个人主页的默认统计范围，通常跨越 13 个自然月。
- 仓库贡献行：每行对应一个参与过的可见仓库，每个色块表示该仓库当月的全部贡献量。
- 相对强度：使用 4 个强度等级区分活跃程度，空月份显示为主题色轨道。
- 贡献重心：按 GitHub「Last year」范围内的总贡献量展示前 5 个仓库，其余内容逐月汇总为 `Other`。
- 贡献总数：右侧展示每个仓库在统计周期内的贡献总数。
- 主题适配：同一 SVG 自动响应 GitHub 的浅色与深色模式。
- 缓存处理：使用内容摘要生成版本化文件名，并自动清理旧图。

## 效果预览

<p align="center">
  <img src="examples/preview.svg" alt="GitHub Last year 范围内的仓库贡献重心图">
</p>

## 使用方式

### 1. 在主页 README 中加入占位图片

```html
<p align="left">
  <img src="./contribution-focus.svg" alt="Contribution focus for GitHub's Last year range" />
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

核心步骤如下，运行时会自动解析并检出最新正式版本：

```yaml
- name: Resolve latest contribution focus release
  id: contribution-focus-release
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    release_tag=$(gh api repos/KrelinnBios/github-profile-contribution-focus/releases/latest --jq .tag_name)
    echo tag=$release_tag >> $GITHUB_OUTPUT

- name: Check out contribution focus action
  uses: actions/checkout@v7
  with:
    repository: KrelinnBios/github-profile-contribution-focus
    ref: ${{ steps.contribution-focus-release.outputs.tag }}
    path: .github/actions/github-profile-contribution-focus

- name: Generate contribution focus chart
  id: contribution-focus
  uses: ./.github/actions/github-profile-contribution-focus
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    config-path: contribution-focus.config.json
```

示例工作流每 6 小时自动运行，也支持手动运行；每次运行都会解析最新正式版本，无需配置跨仓库 Token。

## 统计口径

- 数据来自 GitHub GraphQL API 的 `contributionsCollection`。
- 总数以 GitHub 贡献日历为准；可由 GraphQL 归属仓库的 Commit、Issue、Pull Request、Review 和仓库创建贡献会分别计入对应仓库。
- 统计所有参与过且令牌可见的仓库，不限制仓库是否属于本人。
- 统计范围直接采用 GitHub `contributionsCollection` 的默认起止时间，与个人主页「Last year」口径保持一致；首尾月份通常是不完整月份。
- 每个月单独查询，Commit 按每日节点累加，其他类型使用连接总数，避免因逐项分页遗漏月度数据。
- Discussion 或不可见私有贡献等无法安全取得仓库归属的数量会进入 `Other`，不会泄露私有仓库名称。
- 排名按 GitHub「Last year」范围内的总贡献量计算，`Other` 则按月汇总未进入前 5 名或无法归属的贡献。

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
| `github-token` | 是 | 无 | 查询 GitHub 可见贡献数据 |
| `config-path` | 否 | `contribution-focus.config.json` | 配置文件路径 |
| `readme-path` | 否 | `README.md` | 需要更新图片引用的 README |
| `output-directory` | 否 | `.` | SVG 输出目录 |
| `output-prefix` | 否 | `contribution-focus` | 生成文件名前缀 |

### 输出

| 名称 | 说明 |
| --- | --- |
| `image` | 生成的版本化 SVG 路径 |
| `changed` | SVG、README 引用或旧文件是否发生变化 |

## 版本选择与安全

- 最新正式版：推荐使用上方工作流，通过 Releases API 自动解析并检出最新正式版本。
- 完整版本标签：可从 [Releases](https://github.com/KrelinnBios/github-profile-contribution-focus/releases) 选择并固定，升级时由使用者决定。
- 固定提交 SHA：可获得最严格的供应链可重复性，但需要手动跟进更新。

主页工作流中的 `contents: write` 用于提交生成的 SVG 和 README；Action 本身不会向其他仓库写入内容。

## 本地开发

项目只使用 Python 标准库：

```bash
python -m unittest discover -s tests -v
python examples/generate_preview.py
```

## 许可协议

本项目依据 [MIT License](./LICENSE) 发布，允许使用、修改、分发和商业使用，但须保留许可证与版权声明。

## 反馈与贡献

欢迎通过 [GitHub Issue](https://github.com/KrelinnBios/github-profile-contribution-focus/issues) 提交使用问题、统计口径疑问、功能建议或其他改进建议。
