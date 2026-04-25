#!/usr/bin/env python3
"""A股实时监控脚本 - 检测价格突破、量比异动、技术指标信号"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import time

def get_realtime_quote(codes):
    """获取实时行情"""
    df = ak.stock_zh_a_spot_em()
    return df[df['代码'].isin(codes)]

def check_signals(df, thresholds=None):
    """检测技术信号"""
    if thresholds is None:
        thresholds = {
            'price_change': 5.0,
            'volume_ratio': 2.0,
            'turnover_rate': 10.0,
            'main_net_inflow': 1e8,
        }
    
    signals = []
    for _, row in df.iterrows():
        code = row['代码']
        name = row['名称']
        price_change = row.get('涨跌幅', 0)
        volume_ratio = row.get('量比', 1)
        turnover = row.get('换手率', 0)
        main_inflow = row.get('主力净流入', 0)
        
        alerts = []
        if abs(price_change) >= thresholds['price_change']:
            direction = '📈 大涨' if price_change > 0 else '📉 大跌'
            alerts.append(f"{direction} {price_change:.2f}%")
        
        if volume_ratio >= thresholds['volume_ratio']:
            alerts.append(f"🔊 量比异动 {volume_ratio:.2f}")
            
        if turnover >= thresholds['turnover_rate']:
            alerts.append(f"🔄 高换手 {turnover:.2f}%")
            
        if abs(main_inflow) >= thresholds['main_net_inflow']:
            direction = '💰 主力流入' if main_inflow > 0 else '💸 主力流出'
            alerts.append(f"{direction} {main_inflow/1e8:.2f}亿")
        
        if alerts:
            signals.append({
                'code': code,
                'name': name,
                'price': row.get('最新价', 0),
                'alerts': alerts
            })
    
    return signals

def monitor_stocks(codes, interval=60):
    """监控股票"""
    print(f"🎯 开始监控 {len(codes)} 只股票, 间隔 {interval}秒")
    print("-" * 50)
    
    while True:
        try:
            df = get_realtime_quote(codes)
            signals = check_signals(df)
            
            if signals:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - 发现信号:")
                for s in signals:
                    print(f"  {s['code']} {s['name']} ¥{s['price']:.2f}")
                    for alert in s['alerts']:
                        print(f"    {alert}")
            else:
                print(f"{datetime.now().strftime('%H:%M:%S')} - 无信号", end='\r')
                
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n⏹ 监控已停止")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    codes = ['600519', '000858', '300750']
    monitor_stocks(codes, interval=60)
