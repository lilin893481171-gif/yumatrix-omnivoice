# 使用英伟达官方 PyTorch 镜像 (内置了 PyTorch 2.1.0 和 CUDA 11.8，非常稳)
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# 设置工作目录
WORKDIR /app

# 安装必要的系统底层库 (ffmpeg 是处理音频切片的核心生命线)
RUN apt-get update && apt-get install -y ffmpeg git wget

# 🚀 核心修改：安装网关通信库和音频转码库
RUN pip install runpod requests soundfile

# 🚀 核心修改：直接从 GitHub 拉取 OmniVoice 最新源码并安装
RUN pip install git+https://github.com/k2-fsa/OmniVoice.git

# 把咱们刚才写好的 终极版 handler.py 复制进镜像
COPY handler.py /app/handler.py

# 容器启动命令 (-u 参数保证日志能实时推送到 RunPod 后台，方便我们排错)
CMD [ "python", "-u", "/app/handler.py" ]
