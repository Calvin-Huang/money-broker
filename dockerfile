FROM python:3.8.11
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "bot.py", "--host", "0.0.0.0", "--port", "5000" ]