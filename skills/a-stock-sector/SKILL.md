---
name: a-stock-sector
description: A 股板块资金流分析工具 — 聚焦龙虎榜、北向资金、板块轮动与主力动向。基于 akshare (东方财富数据) 实现。Use for A-share sector analysis, smart money tracking, and rotation strategies.
category: research
tags: [a-stock, sector, capital-flow, longhubang, smart-money, akshare]
---

# A 股板块资金流分析工具包

## 核心功能
本 Skill 用于分析 A 股市场的**板块效应**和**主力资金动向**，辅助判断市场热点与持续性。

## 数据获取与 API (注意网络环境)
**重要**: 本工具主要依赖 **东方财富 (East Money)** 数据源。
- **国内网络/本地环境**: 直接调用 `akshare` 接口。
- **受限服务器环境 (如海外云主机)**: 东方财富 API (`push2his.eastmoney.com`) 常被屏蔽。若 `ak.stock_sector_*` 报错 (Connection Refused/Empty Reply)，请使用**备选方案**:
  1. **浏览器抓取**: `browser_navigate("https://data.eastmoney.com/bkzj/hy.html")` + `browser_vision` 分析资金流向表格。
  2. **同花顺/新浪**: 部分板块数据可通过新浪财经板块接口获取。

## 常用分析场景与接口

### 1. 板块资金流向 (Sector Capital Flow)
分析行业/概念板块的主力净流入/流出，识别当日或近期热点。
```python
import akshare as ak

# 行业板块资金流 (今日/3日/5日/10日)
# symbol: "今日", "3日", "5日", "10日"
df_industry = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
print(df_industry[["名称", "主力净流入-净额", "主力净流入-净占比", "涨跌幅"]].head(10))

# 概念板块资金流
df_concept = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="概念资金流")
```
**分析逻辑**:
- **持续流入**: 连续 3-5 日主力净流入且板块指数不跌，视为强趋势。
- **背离**: 板块指数上涨但主力资金大幅流出，警惕拉高出货。

### 2. 龙虎榜分析 (Dragon Tiger List)
追踪游资、机构席位动向。
```python
# 龙虎榜详情
# date: "20240425" 格式
df_lhb = ak.stock_lhb_detail_em(start_date="20240401", end_date="20240425")

# 统计常用字段
cols = ["名称", "代码", "解读", "买入总金额", "卖出总金额", "净额"]
# 过滤机构专用席位或知名游资
institution_mask = df_lhb["上榜理由"].str.contains("机构专用")
print(df_lhb[institution_mask][cols].sort_values("净额", ascending=False).head())
```
**分析逻辑**:
- **机构大买**: 龙虎榜显示"机构专用"大幅净买入，通常意味着基本面拐点或主力建仓。
- **游资接力**: 知名游资 (如"作手新一"、"章盟主"关联席位) 接力，多为短线情绪博弈。

### 3. 北向资金 (North-bound Capital - 沪深港通)
外资风向标 (注意：自 2024 年起，实时北向资金数据已暂停披露，仅保留历史或盘后数据)。
```python
# 历史北向资金
df_north = ak.stock_hsgt_fund_flow_summary_em()
# 关注：沪股通净流入、深股通净流入、北向资金合计
```

### 4. 板块轮动与强度 (Sector Rotation)
结合 **RPS (股价相对强度)** 或 **涨跌幅排名** 判断轮动。
```python
# 概念板块行情 (计算涨幅与成交量配合)
df_concept_index = ak.stock_board_concept_name_em()
# 筛选今日涨幅 > 2% 且 换手率活跃 的板块
active_sectors = df_concept_index[
    (df_concept_index['涨跌幅'] > 2) & 
    (df_conject_index['换手率'] > 1) # 假设字段，需根据实际 akshare 版本调整
]
```

## 板块分析实战技巧

### 资金流 + 情绪共振
- **最强信号**: 板块资金大幅净流入 + 板块内多只个股涨停 (板块效应) + 龙虎榜机构买入。
- **虚假繁荣**: 只有资金流入 (可能是对倒) 但板块内个股涨幅不大，或者龙头股已断板。

### 监控脚本示例 (`scripts/sector_flow_monitor.py`)
- **功能**: 每 30 分钟检查一次行业资金流，若某行业主力净流入占比突增 > 5%，触发提醒。
- **输入**: 监控列表 (可选)，或全行业扫描。
- **输出**: `~/a-stock/data/sector_flow_alert.json`

## 注意事项
1. **数据滞后**: 资金流向数据通常基于 Level-2 大单统计，存在滞后性，不可作为唯一买入依据。
2. **接口变动**: `akshare` 东方财富接口更新频繁，若运行报错 `KeyError`，通常是东方财富网页改版导致解析失败，需升级 akshare。
3. **停更数据**: 北向资金实时数据自 2024 年 7 月起不再实时公布，历史数据仍可查。

## 关联 Skills
- `a-stock`: 个股技术分析 (MA, MACD, Kline)
- `a-stock-news`: 舆情监控 (验证板块是否有消息面配合)