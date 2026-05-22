import runpod
import base64
import requests
import tempfile
import os

# 👉 引入官方必需的库
from omnivoice import OmniVoice
import torch
import soundfile as sf

# ==========================================
# 🌟 第一步：全局预热区 (冷启动时加载模型)
# ==========================================
print("🚀 正在将 OmniVoice 权重载入 GPU 显存...")

# 加载官方 OmniVoice 模型（自动使用半精度 float16 以节省显存并提速）
model = OmniVoice.from_pretrained(
    "k2-fsa/OmniVoice", 
    device_map="cuda:0", 
    dtype=torch.float16,
    load_asr=True # 如果你不传 ref_text，模型需要 Whisper 来自动识别干声
)

print("✅ OmniVoice 引擎就绪，等待网关指令！")

def download_reference_audio(url, save_path):
    """从图床极速下载参考干声"""
    if not url: 
        return False
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"❌ 下载干声失败: {e}")
        return False

# ==========================================
# ⚡ 第二步：核心路由与推理函数
# ==========================================
def handler(job):
    job_input = job.get('input', {})
    prompt_text = job_input.get('prompt', '')
    ref_audio_url = job_input.get('reference_audio', '')
    
    if not prompt_text:
        return {"error": "缺少关键参数：文案不能为空！"}

    print(f"🎯 任务接入 | 准备生成文案: {prompt_text[:20]}...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ref_audio_path = os.path.join(temp_dir, "ref_audio.wav")
            out_audio_path = os.path.join(temp_dir, "output.wav")
            
            # 1. 尝试下载前端传来的干声
            has_ref = False
            if ref_audio_url:
                has_ref = download_reference_audio(ref_audio_url, ref_audio_path)
            
            # 2. 🚀 引擎轰鸣：调用 OmniVoice 模型生成音频
            if has_ref:
                # 【克隆模式】带有参考音频
                audio_output = model.generate(
                    text=prompt_text, 
                    ref_audio=ref_audio_path
                )
            else:
                # 【自动模式】无参考音频，由模型盲盒生成
                audio_output = model.generate(
                    text=prompt_text
                )
                
            # 官方模型返回的是 numpy 数组列表，取第一个，采样率固定 24kHz
            audio_np = audio_output[0]
            
            # 3. 将矩阵数据保存为 WAV 文件，再转成前端需要的 Base64
            sf.write(out_audio_path, audio_np, 24000)
            
            with open(out_audio_path, "rb") as audio_file:
                audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # 4. 完美封装，返回给前端
            return {
                "status": "success",
                "audio_base64": audio_base64,
                "format": "wav"
            }

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"🚨 推理崩溃:\n{error_detail}")
        return {"error": f"模型推理异常: {str(e)}"}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
