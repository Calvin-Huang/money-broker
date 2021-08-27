FROM python:3.8.11-alpine
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000

ENTRYPOINT [ "python", "bot.py", "--host", "0.0.0.0", "--port", "5000" ]