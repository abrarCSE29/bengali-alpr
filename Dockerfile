FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libc-dev \
    libffi-dev \
    rustc \
    cargo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0

COPY requirements.txt .

RUN grep -v '^pywin32==' requirements.txt > filtered_requirements.txt
RUN grep -v '^pywinpty==' filtered_requirements.txt > final_filtered_requirements.txt
# RUN python -m venv venv
# RUN . venv/bin/activate && pip install --no-cache-dir -r final_filtered_requirements.txt
RUN pip install --no-cache-dir -r final_filtered_requirements.txt

COPY flask_server.py .

EXPOSE 5000

CMD ["python", "flask_server.py"]
