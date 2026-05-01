---
name: a-stock-commodity
description: Query Chinese commodity futures prices (copper, aluminum, gold, silver, etc.) from Sina Finance. Covers SHFE (上期所), DCE (大商所), CZCE (郑商所), and LME international metals.
trigger: User asks about commodity prices, futures quotes, metal prices (铜/铝/金/银/原油等)
---

## 商品期货行情查询方法

### 数据源选择

**首选：浏览器 + Vision（最可靠）**
- API 方式（akshare、新浪 hq.sinajs.cn）多数情况下返回空数据或旧数据
- 浏览器直接访问新浪财经期货页面 + vision 截图提取数据成功率最高

**备用：新浪 API（部分合约可用）**
- `https://hq.sinajs.cn/list=CU2606`（沪铜）
- 返回 GBK 编码的逗号分隔字符串
- 注意：`nf_cu0`（连续合约）经常返回空数据

### 浏览器查询流程

1. **沪铜（上期所）**：`https://finance.sina.com.cn/futures/quotes/CU2606.shtml`
   - CU = 铜，合约格式为 CU + 年月（如 CU2606 = 2026年6月）

2. **伦铜（LME）**：`https://finance.sina.com.cn/money/future/hf.html`

3. **黄金**：`https://finance.sina.com.cn/futures/quotes/AU2606.shtml`

4. **白银**：`https://finance.sina.com.cn/futures/quotes/AG2606.shtml`

5. **原油**：`https://finance.sina.com.cn/futures/quotes/SC2606.shtml`

### Vision 提取步骤

```
1. browser_navigate 到对应期货页面
2. 等待页面加载完成
3. browser_vision(question="Find the main futures quote table. I need: 最新价, 涨跌, 涨跌幅, 今开, 昨结算, 最高, 最低, 成交量, 持仓量, 买价, 卖价")
```

### 常见品种合约代码

| 品种 | 交易所 | 代码示例 | 报价单位 |
|------|--------|----------|----------|
| 沪铜 | 上期所 | CU2606 | 元/吨 |
| 沪铝 | 上期所 | AL2606 | 元/吨 |
| 沪金 | 上期所 | AU2606 | 元/克 |
| 沪银 | 上期所 | AG2606 | 元/千克 |
| 原油 | 上期所 | SC2606 | 元/桶 |
| 螺纹钢 | 上期所 | RB2610 | 元/吨 |
| 铁矿石 | 大商所 | I2609 | 元/吨 |
| 伦铜 | LME | - | 美元/吨 |

### 避坑指南

- **akshare 期货接口基本不可用**：`futures_main_sina`、`futures_dailyprice`、`futures_foreign_hist` 均返回错误或空数据
- **新浪 API 连续合约不可靠**：`nf_cu0` 返回空，需查询具体月份合约
- **合约代码格式**：两位年份+两位月份，如 CU2606（26年6月）
- **页面加载**：新浪财经期货页面数据通过 JS 动态加载，需等待页面完全渲染后再截图
- **交易时间**：沪铜日盘 9:00-11:30, 13:30-15:00；夜盘 21:00-次日1:00