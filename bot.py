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
    # ดึง Port จาก Environment Variable ที่ Render กำหนด (Default คือ 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 🤖 ส่วนของ Bot Logic (รองรับ python-telegram-bot v20+) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "สวัสดีค่ะพี่! น้อง Golden และทีมเอเจ้นท์ทั้ง 6 พร้อมระดมสมองวิเคราะห์ทองให้พี่แล้วค่ะ\n\n"
        "กด /analyze เพื่อเริ่มการประชุมทีมได้เลยค๊า! ✨"
    )

async def analyze_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ส่งข้อความเริ่มต้น
    query_msg = await update.message.reply_text("🔍 กำลังเรียกประชุมทีมเอเจ้นท์... โปรดรอสักครู่นะคะ")

    try:
        # --- 1. รวบรวมข้อมูลดิบ (Data Gathering) ---
        price_data = tools.get_latest_prices()
        portfolio_data = tools.get_portfolio_summary()
        news_data = tools.get_market_context()

        # --- 2. ส่งเอเจ้นท์แต่ละตัวไปทำงาน (Agent Analysis) ---
        # Agent 1: นักสืบราคา
        report_1 = agents.ask_agent("นักสืบราคา", f"ราคาตอนนี้ {price_data}. วิเคราะห์การเปลี่ยนแปลงให้พี่หน่อยค่ะ")
        
        # Agent 2: นักเทคนิค (ดึงค่า spot อย่างปลอดภัย)
        spot_val = price_data.get('spot', 'N/A') if isinstance(price_data, dict) else "N/A"
        report_2 = agents.ask_agent("นักเทคนิค", f"จากราคา Spot ${spot_val} คำนวณแนวรับ-ต้านที่สำคัญให้พี่หน่อยค่ะ")
        
        # Agent 6: ผู้ควบคุมความเสี่ยง
        p_weight = portfolio_data.get('total_weight', 0) if isinstance(portfolio_data, dict) else 0
        p_avg = portfolio_data.get('avg_price', 0) if isinstance(portfolio_data, dict) else 0
        report_6 = agents.ask_agent("ผู้ควบคุมความเสี่ยง", f"พอร์ตพี่มีทอง {p_weight} กรัม ทุนเฉลี่ย {p_avg} บาท ควรระวังอะไรไหมคะ?")

        # --- 3. ส่ง "รายงานย่อย" ให้พี่ดูก่อน (Showcase) ---
        brief_reports = (
            "📝 **บันทึกการประชุมเอเจ้นท์ค๊า:**\n\n"
            f"🕵️ **นักสืบราคา:**\n{report_1}\n\n"
            f"📊 **นักเทคนิค:**\n{report_2}\n\n"
            f"🛡️ **ผู้ควบคุมความเสี่ยง:**\n{report_6}\n\n"
            "--------------------------\n"
            "⌛ *น้อง Golden กำลังสรุปผลลัพธ์สุดท้าย...*"
        )
        
        # แก้ไขข้อความเดิมเพื่อแสดงความคืบหน้า
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=query_msg.message_id,
            text=brief_reports,
            parse_mode=constants.ParseMode.MARKDOWN
        )

        # --- 4. หัวหน้า Golden (Agent 4) สรุปปิดท้าย ---
        final_decision = agents.ask_agent(
            "หัวหน้า Golden", 
            f"จากรายงานของทุกคน:\n1. {report_1}\n2. {report_2}\n3. {report_6}\n\n"
            f"สรุปฟันธงให้พี่หน่อยว่าสถานะตอนนี้ควร 'ซื้อ', 'ขาย' หรือ 'นิ่ง' พร้อมเหตุผลสั้นๆ ค๊า"
        )

        full_summary = (
            f"🏆 **บทสรุปจากน้อง Golden ค๊า!**\n\n"
            f"💰 **ราคา Spot ล่าสุด:** ${spot_val}\n"
            f"💡 **คำแนะนำ:**\n{final_decision}"
        )

        # ส่งข้อความสรุปเป็นข้อความใหม่เพื่อให้พี่เห็นชัดๆ ค่ะ
        await update.message.reply_text(full_summary, parse_mode=constants.ParseMode.MARKDOWN)

    except Exception as e:
        # ถ้าพังตรงไหน ให้แจ้งพี่ทันทีพร้อมรายละเอียด
        error_msg = f"อุ๊ย! ทีมเอเจ้นท์ประชุมต่อไม่ได้ค๊า: {str(e)}"
        if query_msg:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=query_msg.message_id,
                text=error_msg
            )
        else:
            await update.message.reply_text(error_msg)

def main():
    # 1. รัน Web Server แยก Thread เพื่อหลอก Render ว่าเราเป็น Web Service
    threading.Thread(target=run_web, daemon=True).start()

    # 2. เริ่มต้นระบบบอท Telegram
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("Error: ไม่พบ TELEGRAM_TOKEN ใน Environment Variables ค๊า!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    
    # เพิ่มคำสั่งการใช้งาน
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze_gold))

    print("--- น้อง Golden ตื่นแล้วค๊า! เริ่มทำงานบน Render เรียบร้อย ---")
    application.run_polling()

if __name__ == '__main__':
    main()
