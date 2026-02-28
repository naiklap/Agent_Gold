import os
from openai import OpenAI

# ตั้งค่า Client ผ่าน OpenRouter
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

def ask_agent(role_name, prompt, context=""):
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001", # หรือเลือกโมเดลที่พี่ชอบ
        messages=[
            {"role": "system", "content": f"คุณคือ {role_name} ผู้เชี่ยวชาญด้านทองคำ พูดจาฉะฉานและแม่นยำ"},
            {"role": "user", "content": f"Context: {context}\n\nคำถาม/หน้าที่: {prompt}"}
        ]
    )
    return response.choices[0].message.content

# ตัวอย่างการทำงานของเอเจ้นท์
class GoldenTeam:
    def agent_1_tracker(self):
        # ดึงราคาจาก tools.py (สมมติข้อมูล)
        return "ราคาทองโลก: $2030, ทองไทย: 34,200, บาท: 35.50"
    
    def agent_4_leader(self, all_reports):
        return ask_agent("หัวหน้า Golden", f"สรุปข้อมูลจากทีมและตัดสินใจ: {all_reports}")
