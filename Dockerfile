FROM python:3.8-slim-buster
COPY requirements.txt /requirements.txt
COPY rps_calc_server.py /usr/local/bin/
RUN apt-get update -y
RUN pip install -r /requirements.txt
RUN rm -rf /var/lib/apt/lists/*
WORKDIR /usr/local/bin
ENTRYPOINT ["python", "rps_calc_server.py"]
