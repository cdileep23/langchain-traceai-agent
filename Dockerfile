FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY agent /app/agent

ENV AGENT_HOST=0.0.0.0
ENV AGENT_PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --retries=10 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2).status == 200 else 1)"

CMD ["python", "-m", "agent.server"]
