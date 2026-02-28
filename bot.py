import os
import asyncio
import threading
from flask import Flask
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import tools
import agents

# --- 🌐 ส่วนของ Web Server (เพื่อให้ Render แผนฟรีขึ้นสถานะ Live) ---
app = Flask('')

@app.route('/')
def home():
    return "น้อง Golden กำลังเฝ้าทองให้พี่อยู่นะค๊า! ✨"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 🤖 ส่วนของ Bot Logic (รองรับ python-telegram-bot v20+) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "สวัสดีค่ะพี่! น้อง Golden และทีมเอเจ้นท์ทั้ง 6 พร้อมระดมสมองวิเคราะห์ทองให้พี่แล้วค่ะ\n\n"
        "กด /analyze เพื่อเริ่มการประชุมทีมได้เลยค๊า! ✨"
    )

async def analyze_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. ส่งข้อความเริ่มงาน
    await update.message.reply_text("🔍 กำลังเรียกประชุมทีมเอเจ้นท์... น้อง Golden กำลังตามทุกคนให้นะค๊า")

    try:
        # --- ดึงข้อมูล ---
        raw_price = tools.get_latest_prices()
        price_data = raw_price if isinstance(raw_price, dict) else {"spot": "N/A"}
        
        raw_portfolio = tools.get_portfolio_summary()
        portfolio_data = raw_portfolio if isinstance(raw_portfolio, dict) else {"total_weight": 0}

        # --- 2. ส่งเอเจ้นท์วิเคราะห์และ "ส่งแยกข้อความทันที" ---
        
        # Agent 1: นักสืบราคา
        report_1 = agents.ask_agent("นักสืบราคา", f"ราคา: {price_data}")
        await update.message.reply_text(f"🕵️ **รายงานจากนักสืบราคา:**\n\n{report_1}")

        # Agent 2: นักเทคนิค
        report_2 = agents.ask_agent("นักเทคนิค", f"Spot: {price_data.get('spot')}")
        await update.message.reply_text(f"📊 **รายงานจากนักเทคนิค:**\n\n{report_2}")

        # Agent 6: ผู้ควบคุมความเสี่ยง
        report_6 = agents.ask_agent("ผู้ควบคุมความเสี่ยง", f"พอร์ต: {portfolio_data}")
        await update.message.reply_text(f"🛡️ **รายงานจากผู้ควบคุมความเสี่ยง:**\n\n{report_6}")

        # --- 3. หัวหน้า Golden สรุปปิดท้าย ---
        final_decision = agents.ask_agent("หัวหน้า Golden", f"สรุปจากรายงานทั้ง 3 ฉบับด้านบนให้พี่หน่อยค๊า")
        
        await update.message.reply_text(
            f"🏆 **บทสรุปสุดท้ายจากน้อง Golden ค๊า!**\n\n{final_decision}",
            parse_mode=None # ปิด parse_mode เพื่อความปลอดภัยสูงสุดค่ะ
        )

    except Exception as e:
        await update.message.reply_text(f"ฮึบ! บั๊กยังอยู่ค๊า: {str(e)}")
def main():
    # 1. รัน Web Server แยก Thread
    threading.Thread(target=run_web, daemon=True).start()

    # 2. เริ่มต้นระบบบอท Telegram
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("Error: ไม่พบ TELEGRAM_TOKEN ค๊า!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze_gold))

    print("--- น้อง Golden ตื่นแล้วค๊า! เริ่มทำงานบน Render เรียบร้อย ---")
    application.run_polling()

if __name__ == '__main__':
    main()
