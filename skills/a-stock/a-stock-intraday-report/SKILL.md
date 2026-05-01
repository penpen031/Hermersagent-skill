---
name: a-stock-intraday-report
description: 盘中A股观察列表快照报告 — 交易日10:30/14:00运行，含技术面+基本面(Firecrawl)，生成HTML并邮件发送。V2版含PE/PB/市值/财报。
---

# A股盘中分析报告 (Intraday Report)

在每个交易日盘中（10:30 & 14:00）对10只观察列表股票进行快照分析，生成技术面+基本面+资金流报告并通过邮件发送。

## 核心脚本

### V3 — 技术面+基本面+资金流（当前使用 ✅）
- `~/a-stock/scripts/intraday_stock_report_v2.py`（文件名V2但内容已升级至V3）
- 技术面：新浪财经直接HTTP → K线/均线/MACD
- 基本面：Firecrawl并发抓取新浪个股页 → PE/PB/市值/财报
- 资金流：Firecrawl抓取新浪资金流向表格 → 主力买入/卖出/净流入、散户流向
- **输出目录**: `~/a-stock/data/intraday_v3_*.json` + `~/a-stock/data/intraday_v3_*.html`
- **Python环境**: `/tmp/stock_venv/bin/python`

## 观察列表 (10只)
招商轮船(601872)、三一重工(600031)、瑞芯微(603893)、阳光电源(300274)、聚和材料(688503)、陕西旅游(000610)、中国东航(600115)、彤程新材(603650)、铜陵有色(000630)、先导智能(300450)

## V3 执行流程

**阶段1 — 技术面**（串行，每只间隔60秒）：
1. 新浪财经HTTP抓取K线 → 计算MA/MACD
2. 实时行情抓取

**阶段2 — 基本面+资金流**（并发，最多3线程）：
1. `fetch_fundamentals_firecrawl()`: Firecrawl抓取新浪个股页，正则提取PE/PB/总市值/换手率/营收/净利润
2. `fetch_capital_flow_sina()`: Firecrawl抓取新浪同一页面资金流向表格，提取主力买入/卖出/散户数据
3. 合并到对应股票的 `fundamentals{}` 和 `capital_flow{}` 字段

## 数据源状态

### K线/实时行情
- **东方财富**: ❌ 被服务器IP屏蔽 (`RemoteDisconnected`)
- **腾讯财经**: ❌ akshare解析bug (`invalid literal for int()`)
- **新浪财经HTTP**: ✅ 稳定可用

### 基本面（Firecrawl）
- 成功抓取字段示例：`{"pe_ttm": 32.28, "pb": 2.26, "total_mv": 84882000000, "turnover": 2.62, "revenue": 646.7, "net_profit": 13.38}`
- **重要**：新浪财经Markdown表格格式为 `| 市盈率TTM： | 32.28 |`（含 `|` 分隔符），正则需用 `\s*\|\s*` 匹配

### 资金流（Firecrawl）
- 来源：新浪个股页内嵌资金流向表格（`finance.sina.com.cn/realstock/company/{code}/nc.shtml`）
- 表格格式：`| 净流入（万元） | 主力买入 | 主力卖出 | 散户买入 | 散户卖出 |`
- 正则：`r"净流入[（(]万元[）)]\s*\|\s*([\d.-]+)\s*\|\s*([\d.-]+)\s*\|\s*([\d.-]+)\s*\|\s*([\d.-]+)"`
- 计算：主力净流入 = 主力买入 - 主力卖出，散户净流入 = 散户买入 - 散户卖出
- **注意**：东方财富资金流向页（`data.eastmoney.com/fzzx/`）全部返回404，已弃用

## 执行方式

### 手动执行 V3
```bash
cd ~/a-stock && /tmp/stock_venv/bin/python scripts/intraday_stock_report_v2.py
```

### ⚠️ 超时注意事项
脚本总耗时约 **10-12分钟**（10只股票×60秒间隔 + Firecrawl并发 + 邮件发送）。

**推荐执行方式**（前台+600秒超时）：
```python
terminal(command="cd ~/a-stock && FIRECRAWL_API_KEY='xxx' /tmp/stock_venv/bin/python scripts/intraday_stock_report_v2.py 2>&1", timeout=600)
```
前台执行能看到完整的实时进度输出（进度、技术面结果、Firecrawl抓取状态、邮件发送确认）。

**后台执行**（会丢失进度输出）：
```python
terminal(background=True, notify_on_complete=True, command="cd ~/a-stock && /tmp/stock_venv/bin/python scripts/intraday_stock_report_v2.py 2>&1")
```
⚠️ 后台模式下，即使设置 `PYTHONUNBUFFERED=1`，`process.log/poll` 也无法看到输出（Python子进程的stdout重定向问题）。只能等 `notify_on_complete` 通知后检查 `data/` 目录文件验证结果。

### 首次启动延迟
脚本启动后可能3-5秒无输出（Python导入模块），此时 `ps aux | grep stock_report` 确认进程在运行即可，不要误以为卡死。

### 定时任务
- `a-stock-intraday-1030`: 交易日 10:30
- `a-stock-intraday-1400`: 交易日 14:00

## HTML 报告样式 (V3)
- **标头**: 白底黑字 `#000000`，带边框和阴影，标题显示 "A股盘中分析报告 (V3)"
- **均线系统**: 方块横排（flex wrap），绿色=股价在均线上方，红色=下方
- **基本面卡片**: fund-grid显示总市值/EPS/ROE/净利增长，PE/PB以tag显示
- **资金流向卡片**: 黄色背景 `#fff8e1`，两列显示北向资金（暂缺）和主力净流入（红绿配色）
- **股票卡片**: 网格布局 `repeat(auto-fit, minmax(640px, 1fr))`
- QQ邮箱SMTP授权码: `higylpxllhrzbihi`，收件人: `v-rbao@microsoft.com`

## 注意事项
- **必须使用** `/tmp/stock_venv/bin/python`
- 每只股票间隔60秒防止限流
- Firecrawl并发最多3线程，10只约15-30秒完成
- 如果Firecrawl失败，`fundamentals` 为null，不影响技术面报告