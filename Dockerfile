FROM ubuntu:18.04

RUN mkdir -p /usr/local/tts_runner

COPY . /usr/local/tts_runner

WORKDIR /usr/local/tts_runner

RUN apt update && \
    apt install --no-install-recommends -y python3.8 python3.8-distutils default-jre curl && \
    apt clean && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.8 get-pip.py && \
    rm -f get-pip.py && \
    pip3.8 install --no-cache-dir -r requirements.txt -U

EXPOSE 5000

CMD ["python3.8", "runner.py"]