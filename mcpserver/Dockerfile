# mcpserver/Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8001

CMD ["uvicorn", "main:mcp_app", "--host", "0.0.0.0", "--port", "8001"]