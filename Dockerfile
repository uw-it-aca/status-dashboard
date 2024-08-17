FROM python:3.10


ENV LOG_FILE stdout
ENV PYTHONUNBUFFERED 1

ADD . /app
ADD ./setup.py /app
ADD ./requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN groupadd -r acait && useradd -r -g acait acait
RUN chgrp -R acait . && chmod -R g=u .

USER acait

CMD ["python", "status_dashboard/dashboard.py"]
