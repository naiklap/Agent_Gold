import os
import asyncio
import threading
from flask import Flask
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import tools
import agents

# --- 🌐 ส่วนของ Web Server (สำหรับ Render แผนฟรี) ---
app = Flask('')

@app.route('/')
def home():
    return "น้อง Golden กำลังเฝ้าทองให้พี่อยู่นะค๊า! ✨"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 🤖 ส่วนของ Bot Logic (รองรับ v20+ และ Python 3.13+) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("สวัสดีค่ะพี่! น้อง Golden และทีมเอเจ้นท์พร้อมวิเคราะห์ทองแล้วค๊า\nกด /analyze ได้เลยนะคะ ✨")

async def analyze_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_msg = await update.message.reply_text("🔍 กำลังเรียกประชุมทีมเอเจ้นท์... โปรดรอสักครู่นะคะ")

    try:
        # ดึงข้อมูลจาก Google Sheets
        price_data = tools.get_latest_prices()
        portfolio_data = tools.get_portfolio_summary()
        
        # เอเจ้นท์วิเคราะห์ (ผ่าน OpenRouter)
        report_1 = agents.ask_agent("นักสืบราคา", f"ราคาตอนนี้ {price_data}")
        report_6 = agents.ask_agent("ผู้ควบคุมความเสี่ยง", f"พอร์ตพี่มีทองทุน {portfolio_data.get('avg_price', 0)} บาท")

        final_decision = agents.ask_agent(
            "หัวหน้า Golden", 
            f"สรุปคำแนะนำจากราคา {price_data} และพอร์ตพี่หน่อยค๊า"
        )

        full_message = (
            f"🏆 **รายงานจากทีม Golden ค๊า!**\n\n"
            f"💰 **ราคา Spot:** ${price_data.get('spot', 'N/A')}\n"
            f"💡 **บทสรุป:**\n{final_decision}"
        )

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=query_msg.message_id,
            text=full_message,
            parse_mode=constants.ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"อุ๊ย! เกิดข้อผิดพลาดตอนวิเคราะห์ค๊า: {str(e)}")

def main():
    # 1. รัน Web Server แยก Thread (ต้องมีเพื่อให้ Render ขึ้น Live)
    threading.Thread(target=run_web, daemon=True).start()

    # 2. รันบอท Telegram
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze_gold))

    print("น้อง Golden ตื่นแล้วค๊า...")
    application.run_polling()

if __name__ == '__main__':
    main()
