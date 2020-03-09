# RACAI - RoTTS
Romanian text-to-speech toy engine built using the following tools provided by [ICIA](http://www.racai.ro/) on the back-end:

* Modular Language Processing for Lightweight Applications (MLPLA)
* Speech Synthesis for Lightweight Applications (SSLA)

Very useful resource if you need some fast and cheap Romanian speech synthesis work done for your project

## Installing and running
Either install the python requirements and start the Flask web application

```
pip install -r requirements.txt
python runner.py
```

or use the provided Dockerfile to build an image and run it in a container

```
docker build -t racai/rotts .
docker run -p 5000:5000 racai/rotts
```
