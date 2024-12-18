# 使用 Python 3.9 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY requirements.txt .
COPY main.py .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 运行脚本
CMD ["python", "main.py"] 