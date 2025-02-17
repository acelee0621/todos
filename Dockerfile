# -------------- 构建阶段 --------------
    FROM python:3.13-alpine AS builder

    WORKDIR /
    
    # 复制项目依赖文件（避免复制整个 .venv）
    COPY pyproject.toml uv.lock ./
    
    # 安装 uv
    RUN pip install uv
    
    # 创建虚拟环境并安装依赖
    RUN uv venv && uv sync
    
    # 复制项目代码
    COPY . .
    
    # -------------- 运行阶段 --------------
    FROM python:3.13-alpine
    
    WORKDIR /
    
    # 只复制构建好的 `.venv`
    COPY --from=builder /.venv /.venv
    
    # 复制应用代码（不包含本机的 .venv）
    COPY --from=builder / .
    
    # 设置环境变量，使用 Docker 内部的 Python 运行环境
    ENV PATH="/.venv/bin:$PATH"
    
    
    # 运行 FastAPI 应用
    CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
