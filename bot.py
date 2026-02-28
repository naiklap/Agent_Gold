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
    query_msg = await update.message.reply_text("🔍 กำลังเรียกประชุมทีมเอเจ้นท์... โปรดรอสักครู่นะคะ")

    try:
        # --- 1. รวบรวมข้อมูล ---
        raw_price = tools.get_latest_prices()
        price_data = raw_price if isinstance(raw_price, dict) else {"spot": "N/A", "raw": str(raw_price)}
        
        raw_portfolio = tools.get_portfolio_summary()
        portfolio_data = raw_portfolio if isinstance(raw_portfolio, dict) else {"total_weight": 0, "avg_price": 0}

        # --- 2. ส่งเอเจ้นท์วิเคราะห์ ---
        report_1 = agents.ask_agent("นักสืบราคา", f"ราคา: {price_data}")
        report_2 = agents.ask_agent("นักเทคนิค", f"Spot: {price_data.get('spot')}")
        report_6 = agents.ask_agent("ผู้ควบคุมความเสี่ยง", f"พอร์ต: {portfolio_data}")

        # --- 3. แสดงรายงานย่อย (ปิด ParseMode เพื่อความปลอดภัย) ---
        brief_reports = (
            "📝 บันทึกการประชุมเอเจ้นท์:\n\n"
            f"🕵️ นักสืบ: {report_1}\n\n"
            f"📊 เทคนิค: {report_2}\n\n"
            f"🛡️ ความเสี่ยง: {report_6}\n"
            "--------------------------"
        )
        # ส่งแบบข้อความธรรมดา (ไม่ใส่ parse_mode) เพื่อป้องกันสัญลักษณ์พิเศษทำพิษค๊า
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=query_msg.message_id,
            text=brief_reports
        )

        # --- 4. สรุปฟันธง ---
        final_decision = agents.ask_agent("หัวหน้า Golden", f"สรุปจาก: {report_1}, {report_2}, {report_6}")
        
        full_summary = f"🏆 **บทสรุปจากน้อง Golden**\n\n{final_decision}"
        
        # ตรงสรุปผล น้องจะใช้ MarkdownV2 แบบระมัดระวัง หรือส่งธรรมดาก็ได้ค่ะ
        await update.message.reply_text(full_summary)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        error_text = f"ฮึบ! บั๊กยังอยู่ค๊า: {str(e)}"
        await update.message.reply_text(error_text)
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
