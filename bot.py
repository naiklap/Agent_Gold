import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import tools  # ไฟล์ที่เราเขียนเชื่อม Google Sheets
import agents # ไฟล์ที่รวมฟังก์ชัน ask_agent

def start(update: Update, context: CallbackContext):
    update.message.reply_text("สวัสดีค่ะพี่! น้อง Golden และทีมเอเจ้นท์ทั้ง 6 พร้อมวิเคราะห์ทองจาก Google Sheets ของพี่แล้วค่ะ\n\nกด /analyze เพื่อเริ่มการระดมสมองค๊า! ✨")

def analyze_gold(update: Update, context: CallbackContext):
    query_msg = update.message.reply_text("🔍 กำลังเรียกประชุมทีมเอเจ้นท์... โปรดรอสักครู่นะคะ")

    # --- STEP 1: รวบรวมข้อมูลดิบ (Data Gathering) ---
    price_data = tools.get_latest_prices()        # จากหน้า GoldHistory
    portfolio_data = tools.get_portfolio_summary() # จากหน้า พอร์ตทอง
    news_data = tools.get_market_context()         # ข่าวเศรษฐกิจ

    # --- STEP 2: เอเจ้นท์แต่ละตัววิเคราะห์ตามหน้าที่ ---
    # Agent 1: วิเคราะห์ราคา
    report_1 = agents.ask_agent("นักสืบราคา", f"ราคาตอนนี้ {price_data}. เทียบกับข้อมูลเดิม พุ่งหรือดิ่ง?")
    
    # Agent 2: วิเคราะห์เทคนิค (คำนวณแนวรับ-ต้าน)
    report_2 = agents.ask_agent("นักเทคนิค", f"จากราคา Spot ${price_data['spot']} คำนวณแนวรับ-ต้านที่สำคัญ 3 ระดับ")
    
    # Agent 3 & 5: ข่าวและ Sentiment
    report_3_5 = agents.ask_agent("เจ้ากรมข่าว & Sentiment", f"วิเคราะห์ข่าวนี้: {news_data} ตลาดกลัวหรือกล้า?")
    
    # Agent 6: วิเคราะห์ความเสี่ยง (ดูพอร์ตจริงของพี่)
    report_6 = agents.ask_agent("ผู้ควบคุมความเสี่ยง", f"พี่มีทอง {portfolio_data['total_weight']} กรัม ทุนเฉลี่ย {portfolio_data['avg_price']} บาท. สถานะตอนนี้ควรทำอย่างไร?")

    # --- STEP 3: หัวหน้า Golden (Agent 4) สรุปและตัดสินใจ ---
    all_reports = f"ราคา: {report_1}\nเทคนิค: {report_2}\nข่าว: {report_3_5}\nความเสี่ยง: {report_6}"
    
    final_decision = agents.ask_agent(
        "หัวหน้า Golden", 
        f"จากรายงานทั้งหมดนี้ สรุปคำแนะนำให้พี่แบบสั้น กระชับ และบอกว่าควร 'ซื้อ-ขาย-หรือนิ่ง' พร้อมเหตุผลค๊า\n\n{all_reports}"
    )

    # --- STEP 4: ส่ง Flex Message สรุปให้พี่ ---
    full_message = (
        f"🏆 **รายงานจากทีม Golden ค๊า!**\n\n"
        f"💰 **ราคา Spot:** ${price_data['spot']}\n"
        f"🏢 **ทองไทย (ขาย):** {price_data['hsh_sell']} บาท\n"
        f"📦 **พอร์ตพี่:** {portfolio_data['total_weight']:.2f} กรัม (ทุน {portfolio_data['avg_price']:,.0f})\n"
        f"--------------------------\n"
        f"💡 **บทสรุป:**\n{final_decision}"
    )

    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=query_msg.message_id,
        text=full_message,
        parse_mode=ParseMode.MARKDOWN
    )

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("analyze", analyze_gold))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
