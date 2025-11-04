FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn
ENV PYWEBFORGE_KEYS=admin:dev-admin,editor:dev-editor,viewer:dev-viewer EgressDeny=1
EXPOSE 7860
CMD ["gunicorn","-w","2","-b","0.0.0.0:7860","backend.app:app"]
