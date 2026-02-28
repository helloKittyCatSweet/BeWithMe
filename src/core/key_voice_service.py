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

def create_custom_voice(file_path, voice_name="MyKin", description="Family member voice for BeWithMe project"):
    """
    🧬 关键功能：上传音频文件到 ElevenLabs 并返回生成的 voice_id
    
    Args:
        file_path: 音频文件路径 (支持 .mp3, .wav, .m4a)
        voice_name: 音色名称
        description: 音色描述
    
    Returns:
        voice_id: 成功返回音色ID，失败返回 None
    """
    print(f"🧬 正在克隆音色: {voice_name}...")
    print(f"   文件: {file_path}")
    
    try:
        # 使用 ElevenLabs SDK 的 voices.add 方法
        voice = el_client.voices.add(
            name=voice_name,
            description=description,
            files=[file_path],  # 支持上传多个文件以提高质量
        )
        
        voice_id = voice.voice_id
        print(f"✅ 音色创建成功！")
        print(f"   Voice ID: {voice_id}")
        print(f"   ⚠️  建议保存此 ID，用于后续对话")
        
        return voice_id
        
    except Exception as e:
        print(f"❌ 克隆失败: {e}")
        print(f"   提示: 确保音频文件清晰、背景安静，时长建议 30 秒以上")
        return None


def delete_custom_voice(voice_id):
    """
    🗑️ 删除自定义音色（释放 API 配额）
    
    Args:
        voice_id: 要删除的音色ID
    
    Returns:
        bool: 成功返回 True
    """
    print(f"🗑️ 正在删除音色: {voice_id}...")
    try:
        el_client.voices.delete(voice_id)
        print(f"✅ 音色删除成功")
        return True
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        return False


def list_available_voices():
    """
    📋 列出所有可用音色（包括克隆的）
    
    Returns:
        list: 音色列表
    """
    try:
        voices = el_client.voices.get_all()
        print(f"📋 当前可用音色数: {len(voices.voices)}")
        
        for v in voices.voices:
            category = "🧬 克隆" if v.category == "cloned" else "🎭 预设"
            print(f"   {category} | {v.name} | ID: {v.voice_id}")
        
        return voices.voices
        
    except Exception as e:
        print(f"❌ 获取音色列表失败: {e}")
        return []


def text_to_speech(text, voice_id=None, output_path="output.mp3"):
    """
    🎙️ 增强版 TTS：支持自定义 voice_id
    
    Args:
        text: 要合成的文本
        voice_id: 音色ID（默认使用环境变量中的）
        output_path: 输出文件路径
    
    Returns:
        str: 成功返回文件路径，失败返回 None
    """
    target_voice = voice_id or VOICE_ID
    print(f"🎙️ 正在合成语音: {text[:20]}...")
    print(f"   使用音色: {target_voice}")
    
    try:
        # 1. 获取响应（注意：这是一个上下文管理器）
        response = el_client.text_to_speech.convert(
            text=text,
            voice_id=target_voice,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        
        # 2. 手动迭代并写入文件
        with open(output_path, "wb") as f:
            # response 在这里是一个生成器，需要循环读取内容
            for chunk in response:
                if chunk:
                    f.write(chunk)
        
        print(f"✅ 成功！语音已保存至: {output_path}")
        
        # 3. (可选) 如果你系统有 ffmpeg 且想尝试播放，可以取消下面注释
        # os.system(f"ffplay -nodisp -autoexit {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ ElevenLabs 报错: {e}")
        return None
    

# --- 快速测试 ---
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🎯 Be With Me - 音色克隆 + 模拟通话测试")
    print("=" * 60)
    
    # 测试模式选择
    mode = sys.argv[1] if len(sys.argv) > 1 else "chat"
    
    if mode == "clone":
        # 测试音色克隆
        print("\n📁 请提供音频文件路径（或使用示例）:")
        audio_path = input("音频路径 (直接回车使用测试): ").strip()
        
        if audio_path and os.path.exists(audio_path):
            voice_name = input("音色名称 (例如: 奶奶): ").strip() or "MyKin"
            voice_id = create_custom_voice(audio_path, voice_name)
            
            if voice_id:
                print(f"\n🎉 克隆成功！现在可以用这个 voice_id 进行对话: {voice_id}")
                print(f"   建议: 将此 ID 保存到 .env 文件中")
                print(f"   ELEVEN_VOICE_ID={voice_id}")
        else:
            print("⚠️  未提供有效的音频文件")
    
    elif mode == "list":
        # 列出所有音色
        print("\n📋 正在获取音色列表...")
        list_available_voices()
    
    elif mode == "delete":
        # 删除音色
        voice_id = input("要删除的 voice_id: ").strip()
        if voice_id:
            delete_custom_voice(voice_id)
    
    else:
        # 默认: 测试对话
        print("\n🧪 测试模式: 模拟通话")
        print("-" * 60)
        
        test_prompt = "你是一位慈祥的奶奶，说话总是带着关怀和温暖。"
        test_user_input = "奶奶，我今天在学校被老师夸奖了！"
        
        # 1. 生成文字
        print(f"\n👤 用户: {test_user_input}")
        ai_text = generate_kin_response(test_user_input, test_prompt)
        print(f"👵 AI 回复: {ai_text}")
        
        # 2. 生成语音
        audio_file = text_to_speech(ai_text, output_path="test_grandma.mp3")
        
        if audio_file:
            print(f"\n✅ 完整流程测试成功！")
            print(f"   音频文件: {audio_file}")
            print(f"\n💡 提示: 你可以用以下命令测试克隆:")
            print(f"   python {__file__} clone")
