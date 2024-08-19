FROM python:3.10

ENV LOG_FILE stdout
ENV PYTHONUNBUFFERED 1

RUN groupadd -r acait && useradd -r -g acait acait

ADD . /app
RUN chgrp -R acait /app && chmod -R g=u /app

ADD --chown=acait:acait ./setup.py /app/
ADD --chown=acait:acait ./requirements.txt /app/
ADD --chown=acait:acait ./docker/ready.sh /scripts/
RUN chmod u+x /scripts/ready.sh

WORKDIR /app

RUN pip install -r requirements.txt

USER acait

CMD ["python", "status_dashboard/dashboard.py"]
