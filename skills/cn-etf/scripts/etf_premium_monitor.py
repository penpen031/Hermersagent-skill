"""
ETF 溢价率监控脚本
筛选高溢价或低折价的 ETF
"""
import akshare as ak
import pandas as pd
import json
from datetime import datetime

def monitor_etf_premium():
    print(f"⏳ 获取 ETF 实时行情数据...")
    try:
        # 获取 ETF 实时行情 (东方财富源)
        df = ak.fund_etf_spot_em()
        
        # 假设字段包含: 代码，名称，最新价，IOPV 实时净值，溢价率
        # 如果 akshare 版本不同，字段名可能需要调整
        # 通常会有 '溢价率' 这一列
        
        if '溢价率' in df.columns:
            # 筛选溢价率 > 2% 的品种
            df_high_premium = df[df['溢价率'] > 2.0].sort_values(by='溢价率', ascending=False)
        elif '涨跌额' in df.columns:
            # 若无直接溢价率字段，可能需要自行计算 (需 IOPV 数据)
            # 此处简化为展示涨跌幅前 10
            df_high_premium = df.sort_values(by='涨跌幅', ascending=False).head(10)
        else:
            df_high_premium = df.head(10)
            
        result = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "alert_type": "High Premium ETF",
            "threshold": 2.0,
            "data": df_high_premium.to_dict(orient='records')
        }
        
        with open('~/a-stock/data/etf_premium.json', 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print("✅ ETF 溢价监控数据已更新。")
        print(df_high_premium[['代码', '名称', '最新价', '涨跌幅']].head().to_string())
        
    except Exception as e:
        print(f"❌ 获取失败 (可能是网络受限): {e}")

if __name__ == "__main__":
    monitor_etf_premium()
