import pandas as pd
import matplotlib.pyplot as plt
import datetime
import random
import os

# ==========================================
# 設定區域 (Configuration)
# ==========================================
# 這是你要追蹤的產品清單
TARGET_PRODUCTS = [
    {"id": "DDR4_3200_16GB_Kingston", "name": "Kingston Fury Beast DDR4-3200 16GB"},
    {"id": "DDR4_3600_16GB_GSkill", "name": "G.SKILL Trident Z Neo DDR4-3600 16GB"},
    {"id": "DDR4_3200_32GB_Corsair", "name": "Corsair Vengeance LPX DDR4-3200 32GB"},
]

DATA_FILE = "ram_price_history.csv"
CHART_FILE = "ram_trend.png"
REPORT_FILE = "weekly_report.md"

# ==========================================
# 核心功能函式庫
# ==========================================

def get_price_from_web(product_id):
    """
    [擴充點] 這裡是用來抓取真實網站價格的地方。
    目前設定為 '模擬模式'，會回傳一個隨機波動的價格。
    未來你可以整合 Requests 或 Selenium 來抓取 PChome/Amazon。
    """
    # 模擬基礎價格
    base_price = 0
    if "16GB" in product_id:
        base_price = 1200
    elif "32GB" in product_id:
        base_price = 2300
    
    # 模擬市場波動 (隨機 +- 5%)
    fluctuation = random.uniform(0.95, 1.05)
    return int(base_price * fluctuation)

def generate_mock_history():
    """
    [僅供測試] 如果沒有歷史檔案，產生過去 12 週的假資料讓你測試分析功能。
    """
    print("⚠️ 未偵測到歷史數據，正在生成模擬測試數據...")
    data = []
    today = datetime.date.today()
    
    for week in range(12, 0, -1):
        date = today - datetime.timedelta(weeks=week)
        for product in TARGET_PRODUCTS:
            # 模擬一個隨機價格趨勢
            mock_price = get_price_from_web(product["id"])
            data.append({
                "Date": date.strftime("%Y-%m-%d"),
                "Product_ID": product["id"],
                "Product_Name": product["name"],
                "Price": mock_price
            })
    
    df = pd.DataFrame(data)
    df.to_csv(DATA_FILE, index=False)
    print(f"✅ 已生成模擬數據至 {DATA_FILE}")

def update_prices():
    """
    執行本週的價格更新
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    new_records = []
    
    print(f"📊 正在獲取 {today} 的最新報價...")
    
    for product in TARGET_PRODUCTS:
        price = get_price_from_web(product["id"])
        new_records.append({
            "Date": today,
            "Product_ID": product["id"],
            "Product_Name": product["name"],
            "Price": price
        })
        print(f"   - {product['name']}: ${price}")
        
    # 讀取舊資料並合併
    if os.path.exists(DATA_FILE):
        df_history = pd.read_csv(DATA_FILE)
        df_new = pd.DataFrame(new_records)
        df_updated = pd.concat([df_history, df_new], ignore_index=True)
    else:
        df_updated = pd.DataFrame(new_records)
        
    # 去除重複 (如果同一天跑兩次)
    df_updated.drop_duplicates(subset=["Date", "Product_ID"], keep='last', inplace=True)
    df_updated.to_csv(DATA_FILE, index=False)
    return df_updated

def analyze_and_visualize(df):
    """
    分析趨勢並畫圖
    """
    print("📈 正在進行趨勢分析與繪圖...")
    
    # 確保日期格式正確
    df["Date"] = pd.to_datetime(df["Date"])
    
    # 1. 繪製圖表
    plt.figure(figsize=(10, 6))
    
    for product in TARGET_PRODUCTS:
        product_data = df[df["Product_ID"] == product["id"]]
        plt.plot(product_data["Date"], product_data["Price"], marker='o', label=product["name"])
    
    plt.title("DDR4 RAM Price Trend (12 Weeks)", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Price (TWD)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"✅ 趨勢圖已儲存為 {CHART_FILE}")

    # 2. 計算 WoW (週變動率) 並生成報告
    report_content = f"# 🖥️ DDR4 記憶體週報 ({datetime.date.today()})\n\n"
    report_content += "## 1. 價格變動摘要\n"
    report_content += "| 產品名稱 | 本週價格 | 上週價格 | 漲跌幅 (WoW) | 趨勢 |\n"
    report_content += "|---|---|---|---|---|\n"
    
    for product in TARGET_PRODUCTS:
        p_data = df[df["Product_ID"] == product["id"]].sort_values("Date")
        if len(p_data) >= 2:
            current_price = p_data.iloc[-1]["Price"]
            last_week_price = p_data.iloc[-2]["Price"]
            change = current_price - last_week_price
            percent = (change / last_week_price) * 100
            
            # 判斷趨勢圖示
            if percent > 1: icon = "🔴 漲" # 紅色代表漲 (台股習慣)
            elif percent < -1: icon = "🟢 跌"
            else: icon = "⚪ 持平"
            
            report_content += f"| {product['name']} | ${current_price} | ${last_week_price} | {percent:.2f}% | {icon} |\n"
        else:
             report_content += f"| {product['name']} | ${p_data.iloc[-1]['Price']} | N/A | - | 新增資料 |\n"
    
    report_content += "\n## 2. 分析建議\n"
    report_content += "- **短期趨勢**：請參考附檔趨勢圖。\n"
    report_content += "- **購買建議**：若連續兩週跌幅超過 3%，建議可入手；若價格持平，建議觀望。\n"
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"✅ 分析報告已儲存為 {REPORT_FILE}")

# ==========================================
# 主程式入口
# ==========================================
if __name__ == "__main__":
    # 1. 如果沒有資料檔，先生成模擬資料 (讓你第一次跑就有東西看)
    if not os.path.exists(DATA_FILE):
        generate_mock_history()
    
    # 2. 更新本週價格
    df = update_prices()
    
    # 3. 分析與輸出
    analyze_and_visualize(df)
    
    print("\n🎉 完成！請查看目錄下的 'ram_trend.png' 與 'weekly_report.md'")


