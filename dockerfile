FROM python:3.8.11-alpine

ENV PYTHONUNBUFFERED 1

RUN apk add --update \
  build-base \
  cairo \
  cairo-dev \
  cargo \
  freetype-dev \
  gcc \
  gettext \
  lcms2-dev \
  libffi-dev \
  musl-dev \
  openssl-dev \
  pango-dev \
  py-cffi \
  python3-dev \
  rust \
  tcl-dev \
  tiff-dev \
  tk-dev \
  zlib-dev

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000

ENTRYPOINT [ "python", "bot.py", "--host", "0.0.0.0", "--port", "5000" ]