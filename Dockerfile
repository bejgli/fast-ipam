FROM python:slim-buster

WORKDIR /

COPY ./ /ipam/

RUN pip install --no-cache-dir --upgrade -r /ipam/requirements/dev.txt

WORKDIR /ipam

RUN ./init_app.sh

CMD ["uvicorn", "fastipam.main:app", "--host=0.0.0.0", "--port=80"]
