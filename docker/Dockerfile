FROM python:3.11.0-slim-buster

RUN apt-get update \
    && apt-get install -y g++ \
    build-essential \
    tzdata \
    libpq-dev \
    && apt-get upgrade -y \
    && apt-get clean \
    && sed -i -E 's/(CipherString\s*=\s*DEFAULT@SECLEVEL=)2/\11/' /etc/ssl/openssl.cnf \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONIOENCODIND utf_8

WORKDIR /app/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app/src

COPY . /app
RUN pip install --upgrade pip setuptools
RUN pip install pipenv
RUN pipenv --python 3.11.0
RUN pipenv install

ARG sh_file_name
ENV env_sh_file_name=$sh_file_name

CMD /bin/bash /app/docker/scripts/${env_sh_file_name}
# CMD [ "/bin/bash" ]

EXPOSE 8000
