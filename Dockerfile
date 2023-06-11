FROM python:3.11

WORKDIR /code

COPY ./requirements/prod.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app/ /code/app

CMD ["uvicorn", "fastipam.main:app", "--host=0.0.0.0", "--port=80"]
