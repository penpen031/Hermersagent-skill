#!/usr/bin/env python3
"""A股技术指标分析脚本 - 包含均线系统及MACD深度解析"""

import akshare as ak
import pandas as pd
import numpy as np

def get_kline(code, period="daily", days=300):
    """获取K线数据 (增加天数以计算长期均线如MA233)"""
    try:
        df = ak.stock_zh_a_hist(symbol=code, period=period, adjust="qfq")
        return df.tail(days)
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        return pd.DataFrame()

def calc_indicators(df):
    """计算技术指标"""
    if df.empty: return df
    df = df.copy()
    
    # 移动平均线
    df['MA20'] = df['收盘'].rolling(20).mean()
    df['MA55'] = df['收盘'].rolling(55).mean()
    df['MA60'] = df['收盘'].rolling(60).mean()
    df['MA120'] = df['收盘'].rolling(120).mean()
    df['MA180'] = df['收盘'].rolling(180).mean()
    df['MA233'] = df['收盘'].rolling(233).mean()
    
    # MACD
    exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
    exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
    df['DIF'] = exp1 - exp2
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = 2 * (df['DIF'] - df['DEA'])
    
    # RSI
    delta = df['收盘'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI14'] = 100 - (100 / (1 + rs))
    
    return df

def analyze(code):
    """综合分析"""
    df = get_kline(code)
    if df.empty: return
    df = calc_indicators(df)
    
    if len(df) < 2: return
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    print(f"\n📊 {code} 技术分析")
    print(f"最新收盘: ¥{latest['收盘']:.2f}")
    print(f"日期: {str(latest['日期'])[:10]}")
    
    print(f"\n📈 均线系统 (MA):")
    print(f"  MA20 (月线):   ¥{latest['MA20']:.2f}")
    print(f"  MA55 (斐波那契):¥{latest['MA55']:.2f}")
    print(f"  MA60 (季线):   ¥{latest['MA60']:.2f}")
    print(f"  MA120(半年线): ¥{latest['MA120']:.2f}")
    print(f"  MA180(牛熊线): ¥{latest['MA180']:.2f}")
    print(f"  MA233(年线替): ¥{latest['MA233']:.2f}")
    
    # 均线排列判断
    mas = [latest['MA20'], latest['MA55'], latest['MA120'], latest['MA233']]
    # 去除 NaN 进行比较
    valid_mas = [x for x in mas if not np.isnan(x)]
    if valid_mas == sorted(valid_mas, reverse=True):
        print("  状态: 多头排列 ✅")
    elif valid_mas == sorted(valid_mas):
        print("  状态: 空头排列 ❌")
    else:
        print("  状态: 均线交织震荡")

    print(f"\n📉 MACD 指标:")
    print(f"  DIF: {latest['DIF']:.3f} | DEA: {latest['DEA']:.3f} | 柱: {latest['MACD']:.3f}")
    if prev['DIF'] < prev['DEA'] and latest['DIF'] > latest['DEA']:
        print("  信号: 零轴" + ("上" if latest['DIF'] > 0 else "下") + "金叉 📈")
    elif prev['DIF'] > prev['DEA'] and latest['DIF'] < latest['DEA']:
        print("  信号: 零轴" + ("上" if latest['DIF'] > 0 else "下") + "死叉 📉")
    
    # 背离检测 (简单版：价格新高/新低与MACD背离)
    # 这里仅展示逻辑，具体需要更多历史数据对比
    if latest['DIF'] > 0:
        print("  位置: 水上 (多头市场)")
    else:
        print("  位置: 水下 (空头市场)")
        
    print("\n=== 分析结束 ===")

if __name__ == "__main__":
    # 测试用例：招商轮船 601872
    analyze("601872")
