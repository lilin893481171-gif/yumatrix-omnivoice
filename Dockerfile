# 使用英伟达官方 PyTorch 镜像
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /app

# 1. 补齐底层的系统音频库 libsndfile1 (soundfile 极度依赖它)
RUN apt-get update && apt-get install -y ffmpeg git wget libsndfile1

# 2. 强行拉满火力：升级到 OmniVoice 官方要求的 PyTorch 2.8.0 和 CUDA 12.8
RUN pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --extra-index-url https://download.pytorch.org/whl/cu128
RUN pip install runpod requests soundfile accelerate transformers

# 3. 安装 OmniVoice
RUN pip install git+https://github.com/k2-fsa/OmniVoice.git

COPY handler.py /app/handler.py

# 确保 HuggingFace 下载数十 GB 模型权重时有权限写入缓存目录
ENV HF_HOME="/app/hf_cache"

CMD [ "python", "-u", "/app/handler.py" ]
