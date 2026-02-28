import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.getenv("GOOGLE_SHEET_CREDENTIALS")
    
    if not creds_json:
        raise Exception("ไม่พบ GOOGLE_SHEET_CREDENTIALS ใน Environment Variables ค๊า")
        
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    sheet_id = "1K00NyHY5tcjtrwnm4tj1BrYWkP9OXYgzK8aQDSU0BKw"
    return client.open_by_key(sheet_id)

# --- สำหรับ Agent 1: ดึงราคาล่าสุด ---
def get_latest_prices():
    try:
        ss = get_google_sheet()
        # เปลี่ยนจาก getSheetByName เป็น worksheet ค่ะ
        sheet = ss.worksheet("GoldHistory") 
        data = sheet.get_all_values()
        
        # GAS insertRowBefore(2) หมายถึงข้อมูลใหม่อยู่แถวที่ 2 (index 1)
        latest = data[1] 
        
        return {
            "time": latest[0],
            "spot": latest[1],
            "usdthb": latest[2],
            "hsh_buy": latest[3],
            "hsh_sell": latest[4],
            "diff": latest[7] if len(latest) > 7 else "0"
        }
    except Exception as e:
        print(f"Error get_latest_prices: {e}")
        # คืนค่าเป็น dict เปล่าเพื่อให้ bot.py ไม่พังค๊า
        return {"spot": "N/A", "hsh_sell": "N/A", "error": str(e)}

# --- สำหรับ Agent 6: วิเคราะห์พอร์ต ---
def get_portfolio_summary():
    try:
        ss = get_google_sheet()
        sheet = ss.worksheet("พอร์ตทอง")
        data = sheet.get_all_records()
        
        total_weight = 0
        total_cost = 0
        
        for row in data:
            # --- จุดสำคัญ: เช็กว่าเป็นรายการ 'ซื้อ' หรือ 'ขาย' เท่านั้น ---
            # เพื่อป้องกันไม่ให้ไปดึงแถว "รวม" มาบวกซ้ำค๊า
            type_trade = str(row.get('ประเภท', '')).strip()
            
            if type_trade in ['ซื้อ', 'ขาย']:
                weight = row.get('น้ำหนัก (กรัม)')
                cost = row.get('ราคารวม (บาท)')
                
                if weight and weight != "":
                    # ถ้าเป็น 'ขาย' ให้ลบน้ำหนักออก (ถ้าพี่มีบันทึกขายในอนาคตค๊า)
                    val_w = float(str(weight).replace(',', ''))
                    total_weight += val_w if type_trade == 'ซื้อ' else -val_w
                    
                if cost and cost != "":
                    val_c = float(str(cost).replace(',', ''))
                    total_cost += val_c if type_trade == 'ซื้อ' else -val_c
            
        return {
            "total_weight": round(total_weight, 4),
            "total_cost": round(total_cost, 2),
            "avg_price": (total_cost / total_weight * 15.244) if total_weight > 0 else 0
        }
    except Exception as e:
        print(f"Error get_portfolio_summary: {e}")
        return {"total_weight": 0, "avg_price": 0, "error": str(e)}

# --- สำหรับ Agent 3: ดึงข่าว ---
def get_market_context():
    prices = get_latest_prices()
    # เช็กก่อนว่าเป็น dict ไหม
    if isinstance(prices, dict):
        return f"ขณะนี้ราคาทองสมาคมขายออกที่ {prices.get('hsh_sell')} บาท ตลาด Spot อยู่ที่ ${prices.get('spot')}"
    return "ไม่สามารถดึงข้อมูลตลาดได้ในขณะนี้ค๊า"
