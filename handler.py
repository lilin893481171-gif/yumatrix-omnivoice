import runpod
import base64
import requests
import tempfile
import os
import traceback

print("🚀 容器启动，开始执行全局环境预热...")

model = None
init_error = None

# 🛡️ 架构师的防弹衣：把极其危险的全局加载包起来
try:
    from omnivoice import OmniVoice
    import torch
    import soundfile as sf
    print("✅ 依赖包导入成功，准备从 HuggingFace 拉取 OmniVoice 模型 (这可能需要几分钟)...")
    
    # 自动下载并加载官方模型
    model = OmniVoice.from_pretrained(
        "k2-fsa/OmniVoice", 
        device_map="cuda:0", 
        dtype=torch.float16,
        load_asr=True
    )
    print("✅ OmniVoice 引擎就绪，等待网关指令！")
except Exception as e:
    init_error = traceback.format_exc()
    print(f"🚨 致命错误：全局模型预热失败！\n{init_error}")

def download_reference_audio(url, save_path):
    if not url: return False
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"❌ 下载干声失败: {e}")
        return False

def handler(job):
    # 💡 核心机制：如果容器启动时模型就炸了，直接把错误通过 CF 网关扔回给你的 React 前端！
    if init_error:
        return {"error": f"云端模型加载失败，请检查环境依赖:\n{init_error}"}

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
            
            has_ref = False
            if ref_audio_url:
                has_ref = download_reference_audio(ref_audio_url, ref_audio_path)
            
            # 🚀 引擎轰鸣
            if has_ref:
                audio_output = model.generate(text=prompt_text, ref_audio=ref_audio_path)
            else:
                audio_output = model.generate(text=prompt_text)
                
            audio_np = audio_output[0]
            sf.write(out_audio_path, audio_np, 24000)
            
            with open(out_audio_path, "rb") as audio_file:
                audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
            
            return {
                "status": "success",
                "audio_base64": audio_base64,
                "format": "wav"
            }
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"🚨 推理崩溃:\n{error_detail}")
        return {"error": f"模型推理异常: {error_detail}"}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
