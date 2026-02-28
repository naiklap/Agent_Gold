import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from agents import GoldenTeam

def start(update: Update, context: CallbackContext):
    update.message.reply_text("สวัสดีค่ะ! น้อง Golden พร้อมวิเคราะห์ทองให้พี่แล้วค่ะ กด /analyze เพื่อเริ่มเลย")

def analyze(update: Update, context: CallbackContext):
    team = GoldenTeam()
    update.message.reply_text("🔍 กำลังระดมสมองเอเจ้นท์ทั้ง 6 ตัว... โปรดรอสักครู่ค่ะ")
    
    # 1. สืบราคา
    price_data = team.agent_1_tracker()
    
    # 2. จำลองการถกกัน (ในเวอร์ชันจริงพี่ดึงข่าว/เทคนิคมาใส่ตรงนี้)
    full_context = f"ข้อมูลราคาล่าสุด: {price_data}"
    
    # 4. หัวหน้าสรุป
    final_decision = team.agent_4_leader(full_context)
    
    # ส่งข้อความสรุป
    update.message.reply_text(f"🏆 **ผลการวิเคราะห์จากทีม Golden**\n\n{final_decision}", parse_mode=ParseMode.MARKDOWN)

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("analyze", analyze))
    
    # รันบน Render ต้องใช้ Webhook หรือ Polling (ถ้า Render แนะนำ Polling สำหรับบอทขนาดเล็ก)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
