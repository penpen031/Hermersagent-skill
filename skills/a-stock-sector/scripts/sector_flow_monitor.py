"""
A 股板块资金流监控脚本
扫描行业板块，找出主力资金净流入前 10 的板块
"""
import akshare as ak
import pandas as pd
import json
from datetime import datetime

def monitor_sector_flow():
    print(f"⏳ 获取行业板块资金流数据...")
    try:
        # 获取今日行业板块资金流
        # 注意：此接口依赖东方财富，若服务器网络受限可能失败
        df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
        
        # 提取关键列
        cols = ['名称', '涨跌幅', '主力净流入-净额', '主力净流入-净占比']
        # 根据实际返回字段调整 (akshare 版本不同字段名可能略有差异)
        # 通常包含：序号，名称，最新价，涨跌幅，换手率，主力净流入-净额，主力净流入-净占比...
        
        # 按主力净流入排序
        if '主力净流入-净额' in df.columns:
            df_top = df.sort_values(by='主力净流入-净额', ascending=False).head(10)
        else:
            # 备用排序
            df_top = df.head(10)
            
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": df_top.to_dict(orient='records')
        }
        
        # 保存 JSON
        with open('~/a-stock/data/sector_flow.json', 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print("✅ 板块资金流数据已更新。")
        print(df_top[['名称', '涨跌幅', '主力净流入-净额']].to_string())
        
    except Exception as e:
        print(f"❌ 获取失败 (可能是网络受限): {e}")

if __name__ == "__main__":
    monitor_sector_flow()
