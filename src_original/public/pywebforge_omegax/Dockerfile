FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /srv/pywebforge

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl git tini &&     rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

ENV HOST=0.0.0.0 PORT=5000
EXPOSE 5000

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "app"]
