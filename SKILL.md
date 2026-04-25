---
name: a-stock
description: Chinese A-stock (A股) market analysis toolkit — real-time quotes via East Money/Sina APIs, technical indicators (MA/MACD/RSI/KDJ), financial statement analysis, custom alerts monitoring, and backtesting framework using akshare/tushare. Supports SH/SZ stock codes (600000/000001 format). Use when user asks about A股, 股票, 个股行情, 技术分析, 财报分析, or wants to set up 监控提醒 for Chinese stocks.
category: research
tags: [a-stock, china, stock-market, akshare, tushare, technical-analysis, financial-analysis]
---

# A股分析工具包

## 数据获取优先级 (重要)

### 第一优先级: akshare + 腾讯财经 API (`stock_zh_a_hist_tx`) — 终端可用
**原因**: 服务器出口IP (122.51.9.57) 被东方财富屏蔽，但腾讯财经 API 完全可用。
- `ak.stock_zh_a_hist_tx(symbol="sh601872")` → 返回 2006 年至今的日K线
- **字段**: date, open, close, high, low, amount(成交额)
- **注意**: 没有 volume(成交量)、涨跌幅、换手率。MA 和 MACD 只需收盘价，不受影响。涨跌幅可自行计算。
- 上海股票用 `sh` 前缀，深圳用 `sz` 前缀

### 第二优先级: 浏览器 + Vision 分析 (用于东方财富/K线截图)
- **步骤**:
  1. 使用 `browser_navigate` 访问 `https://quote.eastmoney.com/sh{code}.html` 或 `https://quote.eastmoney.com/sz{code}.html`
  2. 使用 `browser_vision` 分析页面截图，提取 K 线图上的均线数值 (MA5/10/20/60)、MACD 状态、价格、涨跌幅
  3. 使用 `browser_console` 尝试提取 `window.quotedata` 获取基础信息

### 第三优先级: 新浪 API (实时行情)
- `curl` 直接请求: `https://hq.sinajs.cn/list=sh601872`
- 仅实时报价，无历史K线
- 同花顺网页 (`10jqka.com.cn`) 可访问，但 akshare 的 THS 接口不提供个股历史K线

### 第四优先级: tushare (需要Token)
- `ts.set_token('your_token')` → `pro.daily(ts_code='600519.SH')`

## 股票编码规则
- **上海主板**: 600xxx, 601xxx, 603xxx, 605xxx
- **深圳主板**: 000xxx, 001xxx
- **中小板**: 002xxx
- **创业板**: 300xxx, 301xxx
- **科创板**: 688xxx, 689xxx
- **北交所**: 830xxx, 870xxx

## 常用分析模板

### 技术指标计算
```python
import pandas as pd
import numpy as np

# 移动平均线 (关键均线系统)
df['MA20'] = df['收盘'].rolling(20).mean()   # 月线/波段操作/布林中轨
df['MA55'] = df['收盘'].rolling(55).mean()   # 斐波那契/季度线/强支撑压力
df['MA60'] = df['收盘'].rolling(60).mean()   # 季线/中期多空分水岭
df['MA120'] = df['收盘'].rolling(120).mean() # 半年线/机构生命线
df['MA180'] = df['收盘'].rolling(180).mean() # 长期牛熊分界线
df['MA233'] = df['收盘'].rolling(233).mean() # 斐波那契/年线替代/长期趋势

# MACD (指数平滑异同移动平均线)
exp1 = df['收盘'].ewm(span=12, adjust=False).mean() # 快线 (EMA12)
exp2 = df['收盘'].ewm(span=26, adjust=False).mean() # 慢线 (EMA26)
df['DIF'] = exp1 - exp2                             # 差离值
df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean() # 信号线 (EMA9)
df['MACD'] = 2 * (df['DIF'] - df['DEA'])            # 红绿柱

# RSI
delta = df['收盘'].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df['RSI14'] = 100 - (100 / (1 + rs))

# KDJ
low_min = df['最低'].rolling(9).min()
high_max = df['最高'].rolling(9).max()
rsv = (df['收盘'] - low_min) / (high_max - low_min) * 100
df['K'] = rsv.ewm(com=2).mean()
df['D'] = df['K'].ewm(com=2).mean()
df['J'] = 3 * df['K'] - 2 * df['D']
```

### 财报分析关键指标
```python
# 盈利能力: ROE, ROA, 毛利率, 净利率
# 偿债能力: 资产负债率, 流动比率, 速动比率  
# 成长能力: 营收增长率, 净利润增长率
# 营运能力: 总资产周转率, 存货周转率, 应收账款周转率

# 估值指标: PE, PB, PS, PCF
# DCF估值、相对估值(同行业对比)
```

### 关键均线系统解析
- **MA20 (月线)**: 短线波段生命线，跌破通常意味着短期调整开始。
- **MA55 & MA60 (季线)**: 中期趋势分水岭。55 为斐波那契数，往往比 60 更敏感。站上这两条线通常视为中期走强。
- **MA120 (半年线)**: 机构操盘的重要参考线，牛熊转换的初级信号。
- **MA180 & MA233 (牛熊线/年线)**: 长期趋势判断。
  - **MA233**: 斐波那契数列 (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233)，是判断大级别牛熊的终极防线。
  - **多头排列**: MA20 > MA55 > MA120 > MA233 (看涨)
  - **空头排列**: MA20 < MA55 < MA120 < MA233 (看跌)

### MACD 深度用法
- **零轴**: 水上 (零轴上方) 代表多头市场，水下代表空头市场。
- **金叉/死叉**: 零轴上方的金叉为强势买入信号；零轴下方的金叉通常视为反弹。
- **背离**:
  - **顶背离**: 股价创新高，MACD 红柱或 DIF 未创新高 -> 卖出信号。
  - **底背离**: 股价创新低，MACD 绿柱或 DIF 未创新低 -> 买入信号。

### 监控提醒逻辑
```python
# 价格突破: 突破MA20/MA60, 突破前高/前低
# 成交量异动: 量比 > 2, 换手率异常
# 资金流向: 主力净流入/流出阈值
# 技术指标: MACD金叉/死叉, RSI超买(>70)/超卖(<30)
# 涨跌幅: 涨停/跌停预警, 大幅波动(>5%)
```

## 回测框架
```python
# 简单回测示例
def backtest_ma_crossover(df, short_window=5, long_window=20):
    df['short_ma'] = df['收盘'].rolling(short_window).mean()
    df['long_ma'] = df['收盘'].rolling(long_window).mean()
    df['signal'] = 0
    df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
    df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1
    df['returns'] = df['收盘'].pct_change()
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']
    
    total_return = (df['strategy_returns'] + 1).prod() - 1
    sharpe = df['strategy_returns'].mean() / df['strategy_returns'].std() * np.sqrt(252)
    max_drawdown = (df['收盘'] / df['收盘'].cummax() - 1).min()
    
    return {'total_return': total_return, 'sharpe': sharpe, 'max_drawdown': max_drawdown}
```

## 数据来源优先级 (实测结论)
1. **腾讯财经** (`ak.stock_zh_a_hist_tx`) — 终端可用，完整历史K线 (2006年至今)，字段: open/close/high/low/amount
2. **新浪财经** (`hq.sinajs.cn`) — 终端可用，仅实时行情报价
3. **同花顺** (10jqka.com.cn) — 网页可访问，akshare THS 接口提供财务/板块数据，但无个股K线
4. **东方财富** — ❌ 服务器IP被屏蔽 (TLS握手成功但服务器返回 Empty reply)
5. **tushare** — 需要token，作为备选
6. **浏览器方案** — 东方财富网页版 + Vision 截图，用于获取实时MACD/均线图形

## 项目目录结构
```
~/a-stock/
├── scripts/    # Python 脚本 (爬虫、分析、监控、回测)
└── data/       # JSON 数据文件 (每次抓取结果保存至此)
```

## 股票爬虫脚本安全审查清单
执行任何用户提供的股票脚本前，检查以下项目：
- [ ] 无 `os.system`、`subprocess` 等系统命令调用
- [ ] 无 `eval()`、`exec()` 等危险函数
- [ ] 网络请求仅指向公开行情 API (东方财富/新浪)
- [ ] 不读取密码、密钥等敏感信息
- [ ] JSON 保存路径固定 (建议保存到 `~/a-stock/data/`)
- [ ] 请求之间有延时保护 (批量调用间隔 2-3 秒，防止反爬)
- [ ] 异常信息完整打印 (不截断，方便调试)

## 注意事项
- A股交易时间: 9:30-11:30, 13:00-15:00 (工作日)
- T+1交易制度
- 涨跌停限制: 主板±10%, 科创板/创业板±20%
- 数据延迟: 免费API通常有15分钟延迟
- 使用akshare时注意反爬, 不要频繁请求
- 回测时注意前复权/后复权选择