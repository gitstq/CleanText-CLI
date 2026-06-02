<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Rules-548-purple.svg" alt="548 Rules">
</p>

<p align="center">
  <a href="#-项目介绍-简体中文"><b>简体中文</b></a> ·
  <a href="#-簡介-繁體中文"><b>繁體中文</b></a> ·
  <a href="#-introduction-english"><b>English</b></a>
</p>

---

# 🧹 CleanText-CLI

> 轻量级终端 AI 文本风格净化引擎 — 检测并清洗 AI 生成文本中的"AI味"，让文字回归人类本色

---

## 🎉 项目介绍（简体中文）

### 💡 痛点与灵感

随着 AI 写作工具的普及，越来越多的文本充斥着千篇一律的"AI味"——套话开头、空洞修饰、过度包装的措辞。无论是技术博客、产品文档还是日常写作，AI 生成的内容往往缺乏真实感和个性。

**CleanText-CLI** 正是为了解决这一痛点而生。灵感来源于 GitHub Trending 上的热门项目 [stop-slop](https://github.com/hardikpandya/stop-slop)，但 CleanText-CLI 是一个**完全独立自研**的实现，从零构建了完整的检测引擎、评分系统、自动修复能力和交互式界面。

### 🌟 核心价值

- **检测**：548 条精心编写的规则，覆盖英文和中文 AI 文本特征
- **评分**：5 维度量化评估文本质量（1-10 分 + 字母等级）
- **修复**：智能建议 + 一键自动净化，让 AI 文本焕然一新
- **集成**：Git Hook、管道模式、多格式输出，无缝融入开发工作流

### 🔥 自研差异化亮点

| 维度 | 原项目 (stop-slop) | CleanText-CLI |
|------|---------------------|---------------|
| 产品形态 | 仅 Markdown 规则文件 | 完整 CLI 工具 + 可执行程序 |
| 核心功能 | 纯规则列表 | 检测 + 评分 + 自动修复 + 多格式输出 |
| 中文支持 | ❌ 不支持 | ✅ 252 条中文 AI 文本检测规则 |
| 评分系统 | ❌ 无 | ✅ 5 维度量化评分（直接性/节奏/可信度/真实性/密度） |
| 自动修复 | ❌ 无 | ✅ 智能修复建议 + 一键应用 |
| 输出格式 | ❌ 无 | ✅ 终端/JSON/HTML/Markdown |
| 交互界面 | ❌ 无 | ✅ TUI 交互式仪表盘 |
| 开发集成 | ❌ 无 | ✅ Git pre-commit hook |
| 管道支持 | ❌ 无 | ✅ stdin/stdout 管道模式 |
| 外部依赖 | N/A | ✅ 零依赖（纯 Python 标准库） |

---

## ✨ 核心特性

### 🎯 智能检测引擎
- **548 条检测规则**：296 条英文 + 252 条中文，持续更新
- **5 大检测类别**：
  - 🗣️ **陈词滥调短语**：检测 "In today's rapidly evolving"、"随着...的不断发展" 等典型 AI 套话
  - 🏗️ **结构化陈词滥调**：识别二元对比、戏剧化碎片、虚假主体等结构性 AI 模式
  - 📝 **AI 风格句首**：标记 "In..."、"As..."、"With..."、"随着..." 等高频 AI 句式
  - 🤷 **填充词/模糊表达**：发现 "it's important to note"、"值得注意的是" 等无实质内容的表达
  - 💪 **夸大用语**：识别 "revolutionize"、"赋能"、"引领" 等过度包装的词汇

### 📊 多维度评分系统
- **直接性 (Directness)**：文本是否开门见山，避免冗余铺垫
- **节奏 (Rhythm)**：句子长度变化是否自然，避免单调
- **可信度 (Trustworthiness)**：措辞是否克制准确，避免夸大
- **真实性 (Authenticity)**：表达是否自然，避免 AI 味陈词滥调
- **密度 (Density)**：信息是否紧凑，避免空洞

### 🔧 自动修复引擎
- 按置信度分级（高/中/低），智能排序修复建议
- 支持一键自动应用修复，快速净化文本
- 修复前后对比，清晰展示改动

### 📺 交互式 TUI 仪表盘
- 纯 ANSI 终端渲染，零外部依赖
- 实时评分仪表盘 + 检测列表 + 修复建议
- 键盘导航，交互式浏览检测结果

### 🔗 开发工作流集成
- **Git pre-commit hook**：提交前自动检测暂存文件
- **管道模式**：`cat file.md | cleantext analyze --stdin`
- **多格式输出**：终端（彩色）/ JSON / HTML（暗色主题）/ Markdown

---

## 🚀 快速开始

### 环境要求

- **Python 3.8+**（无需安装任何第三方依赖）

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/CleanText-CLI.git
cd CleanText-CLI

# 方式一：直接运行（推荐，零安装）
python cleantext --help

# 方式二：安装为命令行工具
pip install -e .
cleantext --help
```

### 基本使用

```bash
# 📋 分析文件
python cleantext analyze document.md

# 📋 从管道读取
cat article.txt | python cleantext analyze --stdin

# 📊 快速评分
python cleantext score blog-post.md

# 🔧 自动修复
python cleantext fix --stdin < draft.md > cleaned.md

# 📺 交互式仪表盘
python cleantext tui report.md

# 🪝 安装 Git Hook
python cleantext hook install
```

---

## 📖 详细使用指南

### 分析命令

```bash
# 分析英文文件（自动检测语言）
python cleantext analyze essay.md

# 分析中文文件
python cleantext analyze article.md --lang zh

# 输出 JSON 格式（便于程序处理）
python cleantext analyze doc.md --format json -o result.json

# 输出 HTML 报告（暗色主题，可直接浏览器打开）
python cleantext analyze doc.md --format html -o report.html

# 输出 Markdown 格式
python cleantext analyze doc.md --format markdown -o report.md

# 只显示严重级别为 warning 及以上的问题
python cleantext analyze doc.md --severity warning

# 禁用彩色输出
python cleantext analyze doc.md --no-color
```

### 修复命令

```bash
# 修复文件（直接修改原文件）
python cleantext fix document.md

# 从管道修复
python cleantext fix --stdin < input.txt > output.txt

# 修复中文文本
python cleantext fix --stdin --lang zh < draft.md > cleaned.md
```

### Git Hook 集成

```bash
# 安装 pre-commit hook（自动检测 .md/.txt/.rst 文件）
python cleantext hook install

# 安装后，每次 git commit 时会自动检测暂存的文本文件
# 如果检测到 AI 文本问题，会显示警告但不阻止提交
```

### 管道模式示例

```bash
# 与其他工具组合使用
grep -r "content" src/ | python cleantext analyze --stdin --format json

# 在 CI/CD 中使用
python cleantext score README.md --format json | jq '.score.overall'

# 批量处理
for f in docs/*.md; do python cleantext analyze "$f" --format html -o "reports/$(basename $f .md).html"; done
```

### 命令行参数一览

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--lang` | 检测语言：`auto`（自动）/ `en`（英文）/ `zh`（中文） | `auto` |
| `--format` | 输出格式：`terminal` / `json` / `html` / `markdown` | `terminal` |
| `--severity` | 最低报告级别：`info` / `warning` / `error` | `info` |
| `--no-color` | 禁用终端彩色输出 | `false` |
| `--output, -o` | 输出到文件（而非 stdout） | stdout |
| `--stdin` | 从标准输入读取 | `false` |

---

## 💡 设计思路与迭代规划

### 设计理念

CleanText-CLI 遵循 **"零依赖、开箱即用"** 的设计哲学：

1. **纯标准库实现**：不依赖任何第三方包，`git clone` 后即可运行，无需 `pip install`
2. **规则驱动**：检测逻辑完全基于精心编写的规则模式，不依赖外部 AI 服务，确保隐私和离线可用
3. **渐进式净化**：从检测到评分到修复，提供完整的净化链路，用户可按需使用
4. **开发友好**：管道模式、Git Hook、JSON 输出，无缝融入开发者工作流

### 技术选型

- **Python 标准库**：`re`（正则匹配）、`json`（结构化输出）、`html`（HTML 转义）、`argparse`（CLI 解析）、`sys`/`os`（系统操作）
- **ANSI 转义码**：终端彩色输出和 TUI 界面，无需 Rich 等第三方库

### 后续迭代计划

- [ ] **VS Code 扩展版本**：实时检测编辑器中的 AI 文本
- [ ] **更多语言支持**：日语、韩语、西班牙语规则集
- [ ] **自定义规则**：支持用户添加自己的检测规则
- [ ] **配置文件**：`.cleantextrc` 配置文件支持
- [ ] **Web 在线版**：浏览器端文本净化工具
- [ ] **规则集持续更新**：跟踪最新 AI 文本特征趋势

---

## 📦 打包与部署指南

### 作为 Python 包安装

```bash
# 从源码安装
git clone https://github.com/gitstq/CleanText-CLI.git
cd CleanText-CLI
pip install -e .

# 安装后可直接使用 cleantext 命令
cleantext analyze document.md
```

### 作为独立脚本使用

```bash
# 无需安装，直接运行
git clone https://github.com/gitstq/CleanText-CLI.git
cd CleanText-CLI
python cleantext analyze document.md
```

### 兼容环境

| 环境 | 支持情况 |
|------|---------|
| Python 3.8+ | ✅ 完全支持 |
| Linux / macOS / Windows | ✅ 跨平台 |
| Git 2.0+ | ✅ Hook 功能 |
| 需要 pip 安装第三方包 | ❌ 不需要 |

---

## 🤝 贡献指南

欢迎贡献代码、规则或文档！请遵循以下规范：

### 提交 PR

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/my-feature`
3. 提交更改：`git commit -m "feat: add new detection rules"`
4. 推送分支：`git push origin feature/my-feature`
5. 提交 Pull Request

### 提交规范

遵循 [Angular 提交规范](https://www.conventionalcommits.org/)：

- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具链相关

### 反馈问题

请在 [Issues](https://github.com/gitstq/CleanText-CLI/issues) 页面提交，包含：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<p align="center">
  Made with 🧹 by <a href="https://github.com/gitstq">gitstq</a>
</p>

---
---

# 🧹 CleanText-CLI

> 輕量級終端 AI 文本風格淨化引擎 — 偵測並清洗 AI 生成文本中的「AI味」，讓文字回歸人類本色

---

## 🎉 簡介（繁體中文）

### 💡 痛點與靈感

隨著 AI 寫作工具的普及，越來越多的文本充斥著千篇一律的「AI味」——套話開頭、空洞修飾、過度包裝的措辭。無論是技術博客、產品文檔還是日常寫作，AI 生成的內容往往缺乏真實感和個性。

**CleanText-CLI** 正是為了解決這一痛點而生。靈感來源於 GitHub Trending 上的熱門項目 [stop-slop](https://github.com/hardikpandya/stop-slop)，但 CleanText-CLI 是一個**完全獨立自研**的實現，從零構建了完整的偵測引擎、評分系統、自動修復能力和互動式介面。

### 🌟 核心價值

- **偵測**：548 條精心編寫的規則，覆蓋英文和中文 AI 文本特徵
- **評分**：5 維度量化評估文本品質（1-10 分 + 字母等級）
- **修復**：智慧建議 + 一鍵自動淨化，讓 AI 文本煥然一新
- **整合**：Git Hook、管道模式、多格式輸出，無縫融入開發工作流

### 🔥 自研差異化亮點

| 維度 | 原項目 (stop-slop) | CleanText-CLI |
|------|---------------------|---------------|
| 產品形態 | 僅 Markdown 規則檔案 | 完整 CLI 工具 + 可執行程式 |
| 核心功能 | 純規則列表 | 偵測 + 評分 + 自動修復 + 多格式輸出 |
| 中文支援 | ❌ 不支援 | ✅ 252 條中文 AI 文本偵測規則 |
| 評分系統 | ❌ 無 | ✅ 5 維度量化評分（直接性/節奏/可信度/真實性/密度） |
| 自動修復 | ❌ 無 | ✅ 智慧修復建議 + 一鍵應用 |
| 輸出格式 | ❌ 無 | ✅ 終端/JSON/HTML/Markdown |
| 互動介面 | ❌ 無 | ✅ TUI 互動式儀表盤 |
| 開發整合 | ❌ 無 | ✅ Git pre-commit hook |
| 管道支援 | ❌ 無 | ✅ stdin/stdout 管道模式 |
| 外部依賴 | N/A | ✅ 零依賴（純 Python 標準庫） |

---

## ✨ 核心特性

### 🎯 智慧偵測引擎
- **548 條偵測規則**：296 條英文 + 252 條中文，持續更新
- **5 大偵測類別**：
  - 🗣️ **陳詞濫調短語**：偵測 "In today's rapidly evolving"、"隨著...的不斷發展" 等典型 AI 套話
  - 🏗️ **結構化陳詞濫調**：識別二元對比、戲劇化碎片、虛假主體等結構性 AI 模式
  - 📝 **AI 風格句首**：標記 "In..."、"As..."、"With..."、"隨著..." 等高頻 AI 句式
  - 🤷 **填充詞/模糊表達**：發現 "it's important to note"、"值得註意的是" 等無實質內容的表達
  - 💪 **誇大用語**：識別 "revolutionize"、"賦能"、"引領" 等過度包裝的詞彙

### 📊 多維度評分系統
- **直接性 (Directness)**：文本是否開門見山，避免冗餘鋪墊
- **節奏 (Rhythm)**：句子長度變化是否自然，避免單調
- **可信度 (Trustworthiness)**：措辭是否克制準確，避免誇大
- **真實性 (Authenticity)**：表達是否自然，避免 AI 味陳詞濫調
- **密度 (Density)**：資訊是否緊湊，避免空洞

### 🔧 自動修復引擎
- 按置信度分級（高/中/低），智慧排序修復建議
- 支援一鍵自動應用修復，快速淨化文本
- 修復前後對比，清晰展示改動

### 📺 互動式 TUI 儀表盤
- 純 ANSI 終端渲染，零外部依賴
- 即時評分儀表盤 + 偵測列表 + 修復建議
- 鍵盤導航，互動式瀏覽偵測結果

### 🔗 開發工作流整合
- **Git pre-commit hook**：提交前自動偵測暫存檔案
- **管道模式**：`cat file.md | cleantext analyze --stdin`
- **多格式輸出**：終端（彩色）/ JSON / HTML（暗色主題）/ Markdown

---

## 🚀 快速開始

### 環境要求

- **Python 3.8+**（無需安裝任何第三方依賴）

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/CleanText-CLI.git
cd CleanText-CLI

# 方式一：直接運行（推薦，零安裝）
python cleantext --help

# 方式二：安裝為命令列工具
pip install -e .
cleantext --help
```

### 基本使用

```bash
# 📋 分析檔案
python cleantext analyze document.md

# 📋 從管道讀取
cat article.txt | python cleantext analyze --stdin

# 📊 快速評分
python cleantext score blog-post.md

# 🔧 自動修復
python cleantext fix --stdin < draft.md > cleaned.md

# 📺 互動式儀表盤
python cleantext tui report.md

# 🪝 安裝 Git Hook
python cleantext hook install
```

---

## 📖 詳細使用指南

### 分析命令

```bash
# 分析英文檔案（自動偵測語言）
python cleantext analyze essay.md

# 分析中文檔案
python cleantext analyze article.md --lang zh

# 輸出 JSON 格式（便於程式處理）
python cleantext analyze doc.md --format json -o result.json

# 輸出 HTML 報告（暗色主題，可直接瀏覽器打開）
python cleantext analyze doc.md --format html -o report.html

# 輸出 Markdown 格式
python cleantext analyze doc.md --format markdown -o report.md

# 只顯示嚴重級別為 warning 及以上的問題
python cleantext analyze doc.md --severity warning

# 停用彩色輸出
python cleantext analyze doc.md --no-color
```

### 修復命令

```bash
# 修復檔案（直接修改原檔案）
python cleantext fix document.md

# 從管道修復
python cleantext fix --stdin < input.txt > output.txt

# 修復中文文本
python cleantext fix --stdin --lang zh < draft.md > cleaned.md
```

### Git Hook 整合

```bash
# 安裝 pre-commit hook（自動偵測 .md/.txt/.rst 檔案）
python cleantext hook install

# 安裝後，每次 git commit 時會自動偵測暫存的文本檔案
# 如果偵測到 AI 文本問題，會顯示警告但不阻止提交
```

### 管道模式示例

```bash
# 與其他工具組合使用
grep -r "content" src/ | python cleantext analyze --stdin --format json

# 在 CI/CD 中使用
python cleantext score README.md --format json | jq '.score.overall'

# 批次處理
for f in docs/*.md; do python cleantext analyze "$f" --format html -o "reports/$(basename $f .md).html"; done
```

### 命令列參數一覽

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--lang` | 偵測語言：`auto`（自動）/ `en`（英文）/ `zh`（中文） | `auto` |
| `--format` | 輸出格式：`terminal` / `json` / `html` / `markdown` | `terminal` |
| `--severity` | 最低報告級別：`info` / `warning` / `error` | `info` |
| `--no-color` | 停用終端彩色輸出 | `false` |
| `--output, -o` | 輸出到檔案（而非 stdout） | stdout |
| `--stdin` | 從標準輸入讀取 | `false` |

---

## 💡 設計思路與迭代規劃

### 設計理念

CleanText-CLI 遵循 **「零依賴、開箱即用」** 的設計哲學：

1. **純標準庫實現**：不依賴任何第三方套件，`git clone` 後即可運行，無需 `pip install`
2. **規則驅動**：偵測邏輯完全基於精心編寫的規則模式，不依賴外部 AI 服務，確保隱私和離線可用
3. **漸進式淨化**：從偵測到評分到修復，提供完整的淨化鏈路，使用者可按需使用
4. **開發友善**：管道模式、Git Hook、JSON 輸出，無縫融入開發者工作流

### 後續迭代計劃

- [ ] **VS Code 擴充套件版本**：即時偵測編輯器中的 AI 文本
- [ ] **更多語言支援**：日語、韓語、西班牙語規則集
- [ ] **自訂規則**：支援使用者新增自己的偵測規則
- [ ] **設定檔**：`.cleantextrc` 設定檔支援
- [ ] **Web 線上版**：瀏覽器端文本淨化工具
- [ ] **規則集持續更新**：追蹤最新 AI 文本特徵趨勢

---

## 📦 打包與部署指南

### 作為 Python 套件安裝

```bash
git clone https://github.com/gitstq/CleanText-CLI.git
cd CleanText-CLI
pip install -e .
```

### 作為獨立腳本使用

```bash
git clone https://github.com/gitstq/CleanText-CLI.git
cd CleanText-CLI
python cleantext analyze document.md
```

### 相容環境

| 環境 | 支援情況 |
|------|---------|
| Python 3.8+ | ✅ 完全支援 |
| Linux / macOS / Windows | ✅ 跨平台 |
| Git 2.0+ | ✅ Hook 功能 |
| 需要 pip 安裝第三方套件 | ❌ 不需要 |

---

## 🤝 貢獻指南

歡迎貢獻程式碼、規則或文檔！請遵循以下規範：

### 提交 PR

1. Fork 本倉庫
2. 建立特性分支：`git checkout -b feature/my-feature`
3. 提交更改：`git commit -m "feat: add new detection rules"`
4. 推送分支：`git push origin feature/my-feature`
5. 提交 Pull Request

### 提交規範

遵循 [Angular 提交規範](https://www.conventionalcommits.org/)：

- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文檔更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具鏈相關

### 回饋問題

請在 [Issues](https://github.com/gitstq/CleanText-CLI/issues) 頁面提交。

---

## 📄 開源協議

本項目基於 [MIT License](LICENSE) 開源。

---

<p align="center">
  Made with 🧹 by <a href="https://github.com/gitstq">gitstq</a>
</p>

---
---

# 🧹 CleanText-CLI

> A lightweight terminal AI text style purification engine — detect and clean "AI-slop" from your writing, making text human again

---

## 🎉 Introduction (English)

### 💡 The Problem

With the proliferation of AI writing tools, an overwhelming amount of text now carries the unmistakable stamp of AI generation — cliché openings, hollow modifiers, and over-polished phrasing. Whether it's tech blogs, product docs, or everyday writing, AI-generated content often lacks authenticity and personality.

**CleanText-CLI** was born to solve this exact problem. Inspired by the trending GitHub project [stop-slop](https://github.com/hardikpandya/stop-slop), CleanText-CLI is a **completely independent, from-scratch implementation** that builds a full detection engine, scoring system, auto-fix capabilities, and interactive interface from the ground up.

### 🌟 Core Value

- **Detect**: 548 carefully crafted rules covering English and Chinese AI text patterns
- **Score**: 5-dimension quantitative text quality assessment (1-10 scale + letter grade)
- **Fix**: Smart suggestions + one-click auto-purification to refresh AI-generated text
- **Integrate**: Git Hook, pipe mode, multi-format output — seamlessly fits into your dev workflow

### 🔥 What Makes Us Different

| Dimension | stop-slop (Original) | CleanText-CLI |
|-----------|---------------------|---------------|
| Product Form | Markdown rule file only | Full CLI tool + executable |
| Core Features | Rule list only | Detect + Score + Auto-fix + Multi-format output |
| Chinese Support | ❌ No | ✅ 252 Chinese AI text detection rules |
| Scoring System | ❌ No | ✅ 5-dimension scoring (directness/rhythm/trust/authenticity/density) |
| Auto-Fix | ❌ No | ✅ Smart fix suggestions + one-click apply |
| Output Formats | ❌ No | ✅ Terminal/JSON/HTML/Markdown |
| Interactive UI | ❌ No | ✅ TUI interactive dashboard |
| Dev Integration | ❌ No | ✅ Git pre-commit hook |
| Pipe Support | ❌ No | ✅ stdin/stdout pipe mode |
| External Dependencies | N/A | ✅ Zero dependencies (Python stdlib only) |

---

## ✨ Core Features

### 🎯 Smart Detection Engine
- **548 detection rules**: 296 English + 252 Chinese, continuously updated
- **5 detection categories**:
  - 🗣️ **Cliché Phrases**: Detects "In today's rapidly evolving", "delve into", "landscape" and similar AI boilerplate
  - 🏗️ **Structural Clichés**: Identifies binary contrasts, dramatic fragments, fake subjects, and other structural AI patterns
  - 📝 **AI-Style Sentence Starters**: Flags "In...", "As...", "With..." and other high-frequency AI sentence patterns
  - 🤷 **Filler/Hedge Words**: Finds "it's important to note", "notably" and other content-free expressions
  - 💪 **Booster Words**: Identifies "revolutionize", "game-changing", "cutting-edge" and other over-polished vocabulary

### 📊 Multi-Dimensional Scoring System
- **Directness**: Does the text get straight to the point without unnecessary preamble?
- **Rhythm**: Is there natural variation in sentence length, or is it monotonous?
- **Trustworthiness**: Is the language restrained and accurate, or exaggerated?
- **Authenticity**: Does the writing feel natural, or is it full of AI clichés?
- **Density**: Is the information compact, or is the text hollow?

### 🔧 Auto-Fix Engine
- Confidence-based ranking (high/medium/low) for smart fix prioritization
- One-click auto-apply fixes for rapid text purification
- Before/after comparison to clearly show changes

### 📺 Interactive TUI Dashboard
- Pure ANSI terminal rendering, zero external dependencies
- Real-time score gauge + detection list + fix suggestions
- Keyboard navigation for interactive result browsing

### 🔗 Developer Workflow Integration
- **Git pre-commit hook**: Automatically checks staged files before commit
- **Pipe mode**: `cat file.md | cleantext analyze --stdin`
- **Multi-format output**: Terminal (colored) / JSON / HTML (dark theme) / Markdown

---

## 🚀 Quick Start

### Requirements

- **Python 3.8+** (no third-party dependencies needed)

### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/CleanText-CLI.git
cd CleanText-CLI

# Option 1: Run directly (recommended, zero installation)
python cleantext --help

# Option 2: Install as a CLI tool
pip install -e .
cleantext --help
```

### Basic Usage

```bash
# 📋 Analyze a file
python cleantext analyze document.md

# 📋 Read from pipe
cat article.txt | python cleantext analyze --stdin

# 📊 Quick score
python cleantext score blog-post.md

# 🔧 Auto-fix
python cleantext fix --stdin < draft.md > cleaned.md

# 📺 Interactive dashboard
python cleantext tui report.md

# 🪝 Install Git Hook
python cleantext hook install
```

---

## 📖 Detailed Usage Guide

### Analyze Command

```bash
# Analyze English file (auto-detect language)
python cleantext analyze essay.md

# Analyze Chinese file
python cleantext analyze article.md --lang zh

# Output as JSON (for programmatic processing)
python cleantext analyze doc.md --format json -o result.json

# Output as HTML report (dark theme, open in browser)
python cleantext analyze doc.md --format html -o report.html

# Output as Markdown
python cleantext analyze doc.md --format markdown -o report.md

# Only show warnings and above
python cleantext analyze doc.md --severity warning

# Disable colored output
python cleantext analyze doc.md --no-color
```

### Fix Command

```bash
# Fix a file (modifies in place)
python cleantext fix document.md

# Fix from pipe
python cleantext fix --stdin < input.txt > output.txt

# Fix Chinese text
python cleantext fix --stdin --lang zh < draft.md > cleaned.md
```

### Git Hook Integration

```bash
# Install pre-commit hook (auto-checks .md/.txt/.rst files)
python cleantext hook install

# After installation, every git commit will automatically check staged text files
# If AI text issues are detected, warnings are shown but commits are not blocked
```

### Pipe Mode Examples

```bash
# Combine with other tools
grep -r "content" src/ | python cleantext analyze --stdin --format json

# Use in CI/CD
python cleantext score README.md --format json | jq '.score.overall'

# Batch processing
for f in docs/*.md; do python cleantext analyze "$f" --format html -o "reports/$(basename $f .md).html"; done
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--lang` | Detection language: `auto` / `en` / `zh` | `auto` |
| `--format` | Output format: `terminal` / `json` / `html` / `markdown` | `terminal` |
| `--severity` | Minimum report level: `info` / `warning` / `error` | `info` |
| `--no-color` | Disable colored terminal output | `false` |
| `--output, -o` | Write output to file | stdout |
| `--stdin` | Read from standard input | `false` |

---

## 💡 Design Philosophy & Roadmap

### Design Principles

CleanText-CLI follows the **"zero dependencies, ready to run"** philosophy:

1. **Pure Standard Library**: No third-party packages — `git clone` and run, no `pip install` required
2. **Rule-Driven**: Detection logic is entirely based on carefully crafted rule patterns — no external AI services needed, ensuring privacy and offline availability
3. **Progressive Purification**: From detection to scoring to fixing, a complete purification pipeline where users can engage at any level
4. **Developer-Friendly**: Pipe mode, Git Hook, JSON output — seamlessly integrates into developer workflows

### Roadmap

- [ ] **VS Code Extension**: Real-time AI text detection in the editor
- [ ] **More Languages**: Japanese, Korean, Spanish rule sets
- [ ] **Custom Rules**: User-defined detection rules support
- [ ] **Configuration File**: `.cleantextrc` configuration support
- [ ] **Web Version**: Browser-based text purification tool
- [ ] **Continuous Rule Updates**: Tracking the latest AI text pattern trends

---

## 📦 Packaging & Deployment

### Install as Python Package

```bash
git clone https://github.com/gitstq/CleanText-CLI.git
cd CleanText-CLI
pip install -e .
```

### Use as Standalone Script

```bash
git clone https://github.com/gitstq/CleanText-CLI.git
cd CleanText-CLI
python cleantext analyze document.md
```

### Compatibility

| Environment | Support |
|-------------|---------|
| Python 3.8+ | ✅ Full support |
| Linux / macOS / Windows | ✅ Cross-platform |
| Git 2.0+ | ✅ Hook functionality |
| Requires pip install of third-party packages | ❌ Not needed |

---

## 🤝 Contributing

Contributions of code, rules, or documentation are welcome!

### Submitting a PR

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "feat: add new detection rules"`
4. Push the branch: `git push origin feature/my-feature`
5. Submit a Pull Request

### Commit Convention

Following [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation updates
- `refactor:` Code refactoring
- `test:` Test-related
- `chore:` Build/toolchain

### Reporting Issues

Please file on the [Issues](https://github.com/gitstq/CleanText-CLI/issues) page with:
- Problem description
- Steps to reproduce
- Expected behavior
- Actual behavior

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with 🧹 by <a href="https://github.com/gitstq">gitstq</a>
</p>
