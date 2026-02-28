import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

def get_google_sheet():
    # เชื่อมต่อกับ Google Sheet โดยใช้สิทธิ์จาก Environment Variable
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.getenv("GOOGLE_SHEET_CREDENTIALS")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # ใช้ ID ของชีตที่พี่ให้มา (จาก URL ของพี่)
    sheet_id = "1K00NyHY5tcjtrwnm4tj1BrYWkP9OXYgzK8aQDSU0BKw"
    return client.open_by_key(sheet_id)

# --- สำหรับ Agent 1: ดึงราคาล่าสุดจากหน้า GoldHistory ที่ GAS บันทึกไว้ ---
def get_latest_prices():
    try:
        ss = get_google_sheet()
        sheet = ss.getSheetByName("GoldHistory") # ชื่อต้องตรงกับในโค้ด GAS
        data = sheet.get_all_values()
        latest = data[1] # แถวที่ 2 (เพราะ GAS ใช้ insertRowBefore(2))
        
        return {
            "time": latest[0],
            "spot": latest[1],
            "usdthb": latest[2],
            "hsh_buy": latest[3],
            "hsh_sell": latest[4],
            "diff": latest[7]
        }
    except Exception as e:
        return f"Error ดึงราคา: {str(e)}"

# --- สำหรับ Agent 6: วิเคราะห์พอร์ตจากหน้า พอร์ตทอง ---
def get_portfolio_summary():
    try:
        ss = get_google_sheet()
        sheet = ss.getSheetByName("พอร์ตทอง")
        # ดึงข้อมูลทั้งหมดมาคำนวณ (หรือจะให้ Python สรุปใหม่เพื่อความฉลาด)
        data = sheet.get_all_records()
        
        total_weight = 0
        total_cost = 0
        for row in data:
            total_weight += float(row['น้ำหนัก(กรัม)'])
            total_cost += float(row['ยอดเงินรวม'])
            
        return {
            "total_weight": total_weight,
            "total_cost": total_cost,
            "avg_price": (total_cost / total_weight * 15.244) if total_weight > 0 else 0
        }
    except Exception as e:
        return f"Error ดึงพอร์ต: {str(e)}"

# --- สำหรับ Agent 3: ดึงข่าว (ตัวอย่างใช้ดึงจากชีตถ้าพี่มีการเก็บข่าวไว้) ---
def get_market_context():
    # ในอนาคตพี่สามารถเพิ่มฟังก์ชันดึงข่าวจาก API ภายนอกตรงนี้ได้ค่ะ
    prices = get_latest_prices()
    return f"ขณะนี้ราคาทองสมาคมขายออกที่ {prices['hsh_sell']} บาท ตลาด Spot อยู่ที่ ${prices['spot']}"
