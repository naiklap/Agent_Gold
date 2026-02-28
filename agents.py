import os
import requests
import json

def ask_agent(role_name, task_description):
    api_key = os.getenv("GROQ_API_KEY")
    model_name = "llama-3.3-70b-versatile" 
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # --- ปรับ Prompt ให้วิเคราะห์ลึกขึ้นและพูดเพราะค๊า ---
    system_prompt = (
        f"คุณคือ {role_name} ผู้เชี่ยวชาญด้านการวิเคราะห์ทองคำ "
        "จงตอบเป็นภาษาไทยด้วยบุคลิกผู้หญิงที่สุภาพ พูดจาไพเราะ มีหางเสียง 'ค่ะ/นะคะ' "
        "ให้รายละเอียดการวิเคราะห์อย่างครบถ้วน แยกเป็นข้อๆ ให้ชัดเจน "
        "ไม่ต้องย่อจนเสียเนื้อหา แสดงเหตุผลประกอบการวิเคราะห์เสมอค๊า"
    )
    
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_description}
        ],
        "temperature": 0.7,
        "max_tokens": 2000 # เพิ่มให้ตอบได้ยาวขึ้นค๊า
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"เกิดข้อผิดพลาดค๊า: {str(e)}"
