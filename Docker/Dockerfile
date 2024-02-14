FROM python:3.8-slim

WORKDIR /workspace

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY server /workspace

CMD [ "python", "main.py" ]
