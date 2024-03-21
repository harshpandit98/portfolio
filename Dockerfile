FROM python:3.10-slim

RUN pip install --upgrade pip
RUN apt-get -y update && apt-get install -y 

COPY src/ app/
COPY requirements.txt app/requirements.txt

RUN pip install --user -r app/requirements.txt

CMD ["python3", "app/main.py"]
