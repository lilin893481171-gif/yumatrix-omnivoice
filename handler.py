import runpod
import base64
import requests
import tempfile
import os

# 🌟 1. 模拟引入 OmniVoice 核心库
# import torch
# from omnivoice import OmniVoiceModel 

# 🌟 2. 预加载模型到显存
print("正在将 OmniVoice 权重载入 GPU 显存...")
# model = OmniVoiceModel.from_pretrained("k2-fsa/omnivoice")
# model.to("cuda")

def download_reference_audio(url, save_path):
    """从你的 Cloudinary 图床下载用户上传的参考干声"""
    if not url: 
        return False # 排雷：如果没有URL，直接跳过，不报错
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # 检查图床链接是否真的有效
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print("✅ 参考干声下载成功！")
        return True
    except Exception as e:
        print(f"❌ 下载干声失败: {e}")
        return False

def handler(job):
    """
    RunPod 唯一的入口函数
    """
    # 完美契合 RunPod 规范，提取 input 盒子
    job_input = job.get('input', {})
    
    # 获取前端传来的参数
    prompt_text = job_input.get('prompt', '')
    ref_audio_url = job_input.get('reference_audio', '')
    
    print(f"🎯 收到前端任务！准备生成的文案：{prompt_text}")

    # 只要有文案就可以跑，不强制要求上传干声（方便测试）
    if not prompt_text:
        return {"error": "缺少关键参数：要配音的长文案不能为空！"}

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ref_audio_path = os.path.join(temp_dir, "ref_audio.wav")
            out_audio_path = os.path.join(temp_dir, "output.wav")
            
            # 1. 尝试下载干声
            if ref_audio_url:
                download_reference_audio(ref_audio_url, ref_audio_path)
            
            # 2. 🚀 引擎轰鸣 (这里是未来你要填写真正 OmniVoice 推理代码的地方)
            # ... 
            
            # 3. 排雷核心：使用一段绝对合法、浏览器能直接播放的极简 WAV 文件的 Base64 编码
            # 等你接上真模型后，把这个变量替换成你生成的真音频 Base64 即可！
            real_valid_wav_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
            
            # 4. 完美返回给你的 CF Worker 和 前端
            return {
                "status": "success",
                "audio_base64": real_valid_wav_base64,
                "format": "wav"
            }

    except Exception as e:
        return {"error": f"OmniVoice 推理管线崩溃: {str(e)}"}

# 启动 Serverless 监听
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
