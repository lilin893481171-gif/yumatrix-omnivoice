# 使用英伟达官方 PyTorch 镜像
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# 设置工作目录
WORKDIR /app

# 安装必要的系统库 (用于处理音频流)
RUN apt-get update && apt-get install -y ffmpeg git wget

# 安装 RunPod SDK 和 OmniVoice 及相关依赖库
RUN pip install runpod requests
# 实际部署时解开下面的注释，安装 OmniVoice 和它的依赖
# RUN pip install git+https://github.com/k2-fsa/OmniVoice.git
# RUN pip install torch torchaudio soundfile

# 把刚才写的 handler.py 复制进镜像
COPY handler.py /app/handler.py

# 容器启动命令
CMD [ "python", "-u", "/app/handler.py" ]