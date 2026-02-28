import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from mistralai import Mistral
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

load_dotenv()

# 1. 配置
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# 建议 Voice ID: 
# "EXAVITQu4vr4xnSDxMaL" (Bella - 温柔女性) 
# 或去 ElevenLabs 官网选一个你喜欢的
VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "EXAVITQu4vr4xnSDxMaL") 

client = Mistral(api_key=MISTRAL_API_KEY)
el_client = ElevenLabs(api_key=ELEVEN_API_KEY.strip())

def generate_kin_response(text_input, system_prompt):
    """使用 Mistral 7B 生成文本"""
    response = client.chat.complete(
        model="open-mistral-7b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_input}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text, output_path="output.mp3"):
    print(f"🎙️ 正在合成语音: {text[:20]}...")
    try:
        # 1. 获取响应（注意：这是一个上下文管理器）
        response = el_client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        
        # 2. 手动迭代并写入文件
        with open(output_path, "wb") as f:
            # response 在这里是一个生成器，需要循环读取内容
            for chunk in response:
                if chunk:
                    f.write(chunk)
        
        print(f"✅ 成功！奶奶的声音已保存至: {output_path}")
        
        # 3. (可选) 如果你系统有 ffmpeg 且想尝试播放，可以取消下面注释
        # os.system(f"ffplay -nodisp -autoexit {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ ElevenLabs 报错: {e}")
        return None
    

# --- 快速测试 ---
if __name__ == "__main__":
    test_prompt = "你是一位慈祥的奶奶，说话总是带着关怀。"
    test_user_input = "奶奶，我今天在学校被老师夸奖了！"
    
    # 1. 生成文字
    ai_text = generate_kin_response(test_user_input, test_prompt)
    print(f"👵 AI 说: {ai_text}")
    
    # 2. 生成语音
    text_to_speech(ai_text)