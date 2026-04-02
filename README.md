# AI Feed Aggregator 📡

每日自动收集整理 LinkedIn 和 X (Twitter) 上 AI 相关高热度内容的个人聚合工具。

## 架构概览

```
┌─────────────────────────────────────────────────────┐
│                    调度层 (Cron / n8n)                │
│              每天定时触发 pipeline                     │
└──────────────┬──────────────────────────┬───────────┘
               │                          │
    ┌──────────▼──────────┐   ┌───────────▼──────────┐
    │   X (Twitter) 采集   │   │   LinkedIn 采集       │
    │   Apify Actor        │   │   Apify Actor         │
    │   关键词 + 热度过滤   │   │   关键词 + 热度过滤    │
    └──────────┬──────────┘   └───────────┬──────────┘
               │                          │
               └──────────┬───────────────┘
                          │
               ┌──────────▼──────────┐
               │   AI 处理层          │
               │   Claude API         │
               │   • 去重 & 过滤      │
               │   • 主题分类         │
               │   • 中文摘要生成     │
               │   • 关键洞察提取     │
               └──────────┬──────────┘
                          │
               ┌──────────▼──────────┐
               │   存储 & 展示层      │
               │   • JSON 本地存储    │
               │   • React Dashboard  │
               │   • (可选) Notion API │
               └─────────────────────┘
```

## 技术栈

- **数据采集**: Apify (Twitter Scraper + LinkedIn Scraper)
- **AI 处理**: Claude API (claude-sonnet-4-20250514)
- **自动化**: Python 脚本 + Cron / n8n
- **Dashboard**: React + Tailwind
- **存储**: 本地 JSON (MVP) → Notion/飞书 (进阶)

## 快速开始

### Step 1: 环境准备

```bash
# 安装依赖
pip install apify-client anthropic python-dotenv

# 配置 API Keys
cp config/.env.example config/.env
# 编辑 .env 填入你的 API keys
```

### Step 2: 配置关键词和过滤条件

编辑 `config/keywords.json` 自定义你的采集规则。

### Step 3: 运行 Pipeline

```bash
# 单次运行
python scripts/pipeline.py

# 定时运行 (每天早上 8 点)
crontab -e
# 添加: 0 8 * * * cd /path/to/ai-feed-aggregator && python scripts/pipeline.py
```

### Step 4: 查看 Dashboard

```bash
cd dashboard
npm install && npm run dev
```

## 目录结构

```
ai-feed-aggregator/
├── README.md
├── config/
│   ├── .env.example        # API keys 模板
│   └── keywords.json       # 搜索关键词 & 过滤规则
├── scripts/
│   ├── pipeline.py         # 主 pipeline 脚本
│   ├── fetch_x.py          # X 数据采集
│   ├── fetch_linkedin.py   # LinkedIn 数据采集
│   ├── ai_processor.py     # Claude AI 处理
│   └── export_notion.py    # (可选) 导出到 Notion
├── data/
│   └── feeds/              # 每日聚合数据 JSON
└── dashboard/              # React 前端 Dashboard
```
