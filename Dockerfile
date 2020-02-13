FROM python:3.7.6-alpine3.10

RUN adduser -D usr_data

WORKDIR /home/usr_data

COPY requirements.txt requirements.txt

RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY uploads uploads
COPY usr_app.py config.py .env .flaskenv boot.sh ./

RUN chmod +x boot.sh

ENV FLASK_APP usr_app.py

RUN chown -R usr_data:usr_data ./
USER usr_data

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
