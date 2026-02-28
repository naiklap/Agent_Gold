import os
import asyncio
import threading
from flask import Flask
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import tools
import agents

# --- 🌐 ส่วนของ Web Server ---
app = Flask('')

@app.route('/')
def home():
    return "น้อง Golden กำลังเฝ้าทองให้พี่อยู่นะค๊า! ✨"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 🤖 ส่วนของ Bot Logic ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "สวัสดีค่ะพี่! น้อง Golden และทีมเอเจ้นท์ผู้เชี่ยวชาญพร้อมระดมสมองวิเคราะห์ทองให้พี่แล้วค่ะ\n\n"
        "กด /analyze เพื่อเริ่มการประชุมทีมที่เข้มข้นกว่าเดิมได้เลยค๊า! ✨"
    )

async def analyze_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 กำลังเรียกประชุมทีมเอเจ้นท์... รอบนี้มีสายสืบเศรษฐกิจโลกมาร่วมด้วยนะค๊า")

    try:
        # --- 1. รวบรวมข้อมูลพื้นฐาน ---
        raw_price = tools.get_latest_prices()
        price_data = raw_price if isinstance(raw_price, dict) else {"spot": "N/A"}
        
        raw_portfolio = tools.get_portfolio_summary()
        portfolio_data = raw_portfolio if isinstance(raw_portfolio, dict) else {"total_weight": 0}

        # --- 2. ดึงข้อมูลเศรษฐกิจโลก (Macro News) ---
        macro_news = tools.get_macro_news() # พี่อย่าลืมเช็กฟังก์ชันนี้ใน tools.py นะคะ

        # --- 3. เริ่มการประชุมและส่งรายงานแยกข้อความ ---
        
        # Agent 1: นักสืบราคา
        report_1 = agents.ask_agent("นักสืบราคา", f"ราคาปัจจุบัน: {price_data}")
        await update.message.reply_text(f"🕵️ **รายงานจากนักสืบราคา:**\n\n{report_1}")

        # Agent 2: นักเทคนิค
        report_2 = agents.ask_agent("นักเทคนิค", f"Spot: {price_data.get('spot')}")
        await update.message.reply_text(f"📊 **รายงานจากนักเทคนิค:**\n\n{report_2}")

        # Agent 3: สายสืบเศรษฐกิจโลก (NEW!)
        report_macro = agents.ask_agent("สายสืบเศรษฐกิจโลก", f"ข่าวเศรษฐกิจล่าสุด: {macro_news}")
        await update.message.reply_text(f"🌍 **รายงานจากสายสืบเศรษฐกิจโลก:**\n\n{report_macro}")

        # Agent 6: ผู้ควบคุมความเสี่ยง
        report_6 = agents.ask_agent("ผู้ควบคุมความเสี่ยง", f"พอร์ตของพี่: {portfolio_data}")
        await update.message.reply_text(f"🛡️ **รายงานจากผู้ควบคุมความเสี่ยง:**\n\n{report_6}")

        # --- 4. หัวหน้า Golden รวบรวมข้อมูลทั้งหมดมาฟันธง ---
        context_for_boss = (
            f"1. ข้อมูลราคา: {report_1}\n\n"
            f"2. มุมมองเทคนิค: {report_2}\n\n"
            f"3. ปัจจัยเศรษฐกิจโลก: {report_macro}\n\n"
            f"4. สถานะพอร์ต: {report_6}"
        )
        
        final_decision = agents.ask_agent(
            "หัวหน้า Golden", 
            f"นี่คือข้อมูลทั้งหมดจากการประชุมค่ะ:\n{context_for_boss}\n\n"
            "ช่วยสรุป 'ฟันธง' ให้พี่หน่อยค่ะว่า ด้วยปัจจัยโลกและกราฟแบบนี้ พี่ควร ซื้อ/ขาย/นิ่ง พร้อมเหตุผลที่หนักแน่นค๊า"
        )
        
        await update.message.reply_text(
            f"🏆 **บทสรุปสุดท้ายจากน้อง Golden ค๊า!**\n\n{final_decision}"
        )

    except Exception as e:
        await update.message.reply_text(f"ฮึบ! บั๊กยังอยู่ค๊า: {str(e)}")

def main():
    threading.Thread(target=run_web, daemon=True).start()

    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("Error: ไม่พบ TELEGRAM_TOKEN ค๊า!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze_gold))

    print("--- น้อง Golden ตื่นแล้วค๊า! ทีมเอเจ้นท์ชุดใหญ่เริ่มทำงานแล้ว ---")
    application.run_polling()

if __name__ == '__main__':
    main()
