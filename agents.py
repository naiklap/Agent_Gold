import os
import requests
import json

def ask_agent(role_name, task_description):
    api_key = os.getenv("GROQ_API_KEY")
    # เลือกใช้โมเดลฟรีและฉลาดของ Groq ค๊า
    model_name = "llama-3.3-70b-versatile" 
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # กำหนดบุคลิกให้เอเจ้นท์แต่ละตัว
    system_prompt = f"คุณคือ {role_name} ผู้เชี่ยวชาญด้านทองคำ ตอบเป็นภาษาไทยแบบมืออาชีพและกระชับ"
    
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_description}
        ],
        "temperature": 0.7,
        "max_tokens": 1024 # จำกัดไว้หน่อยเพื่อความเสถียรค๊า
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if response.status_code == 200:
            return result['choices'][0]['message']['content']
        else:
            error_msg = result.get('error', {}).get('message', 'Unknown Error')
            return f"ขออภัยค่ะพี่ เกิดข้อผิดพลาดที่ Groq ({role_name}): {error_msg}"
            
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการติดต่อเอเจ้นท์ {role_name}: {str(e)}"
