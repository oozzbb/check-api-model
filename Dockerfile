# 使用官方 Python 运行时作为父镜像
FROM python:3.8-slim-buster

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中的 /app
COPY . /app

# 安装项目所需的任何依赖
# 如果你有 requirements.txt 文件，取消下面这行的注释
RUN pip install --no-cache-dir -r requirements.txt

# 如果没有 requirements.txt，你可以直接在这里安装所需的包
# 例如：RUN pip install --no-cache-dir package1 package2

# 声明容器将监听的端口
EXPOSE 8501

# 运行应用
# 替换 app.py 为你的主 Python 文件名
CMD ["python", "app.py"]
