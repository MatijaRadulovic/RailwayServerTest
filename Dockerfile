FROM python:3.12-slim
WORKDIR /app
COPY server.py index.html ./
EXPOSE 8765
CMD ["python", "server.py"]
