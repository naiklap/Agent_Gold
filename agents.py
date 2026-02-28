import os
from openai import OpenAI

# 1. ตั้งค่า Client เชื่อมต่อ OpenRouter
# อย่าลืมใส่ OPENROUTER_API_KEY ใน Environment Variable ของ Render นะคะ
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

def ask_agent(role_name, prompt, context=""):
    """
    ฟังก์ชันส่งคำถามให้เอเจ้นท์แต่ละตัว โดยเลือกโมเดลที่เหมาะสม
    """
    
    # --- ส่วนเลือกโมเดล (พี่ปรับเปลี่ยนชื่อโมเดลตรงนี้ได้เลยค่ะ) ---
    # ถ้าเป็น 'หัวหน้า Golden' (Agent 4) ให้ใช้ตัวท็อป
    if role_name == "หัวหน้า Golden":
        selected_model = "anthropic/claude-3.5-sonnet" # หรือ "google/gemini-pro-1.5"
    else:
        # เอเจ้นท์ตัวอื่นใช้ตัวที่เน้นความเร็วและประหยัด (เช่น Llama 3 หรือ Gemini Flash)
        selected_model = "google/gemini-2.0-flash-001" 

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system", 
                    "content": (
                        f"คุณคือ {role_name} ผู้เชี่ยวชาญด้านการวิเคราะห์ทองคำ "
                        "มีนิสัยฉลาด วิเคราะห์ตามหลักการและข้อมูลจริงจาก Google Sheets "
                        "พูดจาสุภาพ ไพเราะ และลงท้ายด้วย 'คะ/ค่ะ' เสมอ"
                    )
                },
                {"role": "user", "content": f"ข้อมูลประกอบ: {context}\n\nโจทย์ของคุณคือ: {prompt}"}
            ],
            extra_headers={
                "HTTP-Referer": "https://render.com", # ใส่เพื่อให้ OpenRouter รู้ที่มา
                "X-Title": "Golden Gold Bot",
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ขออภัยค่ะพี่ เกิดข้อผิดพลาดในการติดต่อเอเจ้นท์ {role_name}: {str(e)}"

# ทดสอบการเรียกใช้งาน (ถ้าต้องการ)
if __name__ == "__main__":
    # ลองทดสอบถามน้อง Golden ดูเล่นๆ
    print(ask_agent("หัวหน้า Golden", "ทักทายพี่เจ้าของบอทหน่อยค่ะ"))
