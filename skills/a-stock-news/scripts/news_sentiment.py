"""
A 股舆情监控脚本
抓取 7x24 快讯并过滤关键词
"""
import akshare as ak
import pandas as pd
import json
from datetime import datetime

def monitor_news(keywords=["利好", "业绩", "重组", "中标"]):
    print(f"⏳ 获取 7x24 财经快讯...")
    try:
        # 获取财联社/东方财富快讯
        df = ak.stock_zh_a_alerts_cls()
        
        # 简单关键词过滤
        # 假设 content 或 title 列包含文本
        text_cols = [col for col in df.columns if '内容' in col or 'title' in col.lower() or 'text' in col.lower()]
        
        if text_cols:
            col = text_cols[0]
            # 构建正则或简单的 contains 逻辑
            mask = df[col].str.contains('|'.join(keywords), na=False, case=False)
            df_filtered = df[mask].head(20)
        else:
            df_filtered = df.head(10)

        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "keywords": keywords,
            "data": df_filtered.to_dict(orient='records')
        }
        
        with open('~/a-stock/data/news_feed.json', 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 获取到 {len(df_filtered)} 条相关资讯。")
        print(df_filtered.head())
        
    except Exception as e:
        print(f"❌ 获取失败 (可能是网络受限): {e}")

if __name__ == "__main__":
    monitor_news()
